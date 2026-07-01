import json
import re
import uuid
from datetime import datetime

import pandas as pd
from flask import jsonify, request

from employment_flask_app import db
from employment_flask_app.api import api_bp
from employment_flask_app.api.auth import require_api_key
from employment_flask_app.models import EmploymentData, Forecast
from employment_flask_app.route_functions import predict_employment_data

REQUIRED_TRIGGER_FIELDS = {'region', 'occupation_type', 'no_of_years'}
MAX_YEARS = 10
Z_THRESHOLD = 2.5


@api_bp.get('/health')
def health():
    """Warm-ping endpoint. Unauthenticated so Power Automate can keep the
    Render dyno warm without leaking the API key on a scheduled trigger."""
    return jsonify(status='ok', service='employment-analytics-api'), 200


@api_bp.post('/trigger-forecast')
@require_api_key
def trigger_forecast():
    payload = request.get_json(silent=True) or {}
    missing = REQUIRED_TRIGGER_FIELDS - payload.keys()
    if missing:
        return jsonify(
            error='bad_request',
            message=f'Missing fields: {sorted(missing)}'
        ), 400

    try:
        no_of_years = int(payload['no_of_years'])
    except (TypeError, ValueError):
        return jsonify(
            error='bad_request',
            message='no_of_years must be an integer'
        ), 400
    if not 1 <= no_of_years <= MAX_YEARS:
        return jsonify(
            error='bad_request',
            message=f'no_of_years must be between 1 and {MAX_YEARS}'
        ), 400

    try:
        markdown_result, forecast_df, start, end = predict_employment_data(
            region=payload['region'],
            no_of_years=no_of_years,
            occupation_type=payload['occupation_type'],
            additional_info=payload.get('additional_info'),
            api_key=payload.get('api_key'),
        )
    except Exception as e:
        msg = str(e)
        if 'RESOURCE_EXHAUSTED' in msg or '429' in msg:
            return jsonify(
                error='upstream_quota',
                message='Gemini quota exhausted',
                retry_after=20
            ), 429
        return jsonify(error='upstream_failed', message=msg[:300]), 502

    summary = re.sub(r'<[^>]+>', '', markdown_result).strip()[:1500]
    forecast_rows = forecast_df.to_dict(orient='records') \
        if not forecast_df.empty else []
    anomaly_count = _count_local_anomalies(payload['region'])

    forecast_id = (
        f"f_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
        f"_{uuid.uuid4().hex[:6]}"
    )
    row = Forecast(
        forecast_id=forecast_id,
        region=payload['region'],
        occupation_type=payload['occupation_type'],
        summary=summary,
        payload=json.dumps(forecast_rows),
        start_year=start,
        end_year=end,
    )
    db.session.add(row)
    db.session.commit()

    return jsonify(
        status='success',
        forecast_id=forecast_id,
        region=payload['region'],
        occupation_type=payload['occupation_type'],
        period={'start_year': start, 'end_year': end},
        summary=summary,
        anomalies_detected=anomaly_count > 0,
        anomaly_count=anomaly_count,
        forecast_rows=forecast_rows,
        generated_at=row.generated_at.isoformat() + 'Z',
    ), 200


@api_bp.get('/latest-forecast')
@require_api_key
def latest_forecast():
    region = request.args.get('region')
    occupation_type = request.args.get('occupation_type')
    if not region:
        return jsonify(
            error='bad_request', message='region query param required'
        ), 400

    q = Forecast.query.filter_by(region=region)
    if occupation_type:
        q = q.filter_by(occupation_type=occupation_type)
    row = q.order_by(Forecast.generated_at.desc()).first()
    if row is None:
        return jsonify(
            error='not_found',
            message='No forecast has been generated for this filter yet'
        ), 404

    age_seconds = (datetime.utcnow() - row.generated_at).total_seconds()
    return jsonify(
        **row.to_dict(),
        forecast_rows=json.loads(row.payload),
        age_hours=round(age_seconds / 3600, 2),
    ), 200


@api_bp.get('/anomalies')
@require_api_key
def anomalies():
    region = request.args.get('region')
    if not region:
        return jsonify(
            error='bad_request', message='region query param required'
        ), 400

    rows = EmploymentData.query.filter_by(RegionName=region).all()
    if not rows:
        return jsonify(
            region=region,
            window=request.args.get('window', 'all'),
            anomalies=[],
            checked_at=datetime.utcnow().isoformat() + 'Z',
        ), 200

    df = pd.DataFrame([{
        'Year': r.Year,
        'OccupationType': r.OccupationType,
        'EmploymentPercentage': r.EmploymentPercentage,
    } for r in rows])

    grouped = df.groupby('OccupationType')['EmploymentPercentage']
    df['mean'] = grouped.transform('mean')
    df['std'] = grouped.transform('std').fillna(0.0)
    # Guard against zero-variance groups producing inf/NaN z-scores.
    df['z'] = (df['EmploymentPercentage'] - df['mean']) / df['std'].replace(
        0.0, pd.NA
    )
    outliers = df[df['z'].abs() > Z_THRESHOLD].dropna(subset=['z'])

    return jsonify(
        region=region,
        window=request.args.get('window', 'all'),
        anomalies=[{
            'year': int(row.Year),
            'occupation_type': row.OccupationType,
            'employment_pct': round(row.EmploymentPercentage, 2),
            'expected_range': [
                round(row.mean - Z_THRESHOLD * row.std, 2),
                round(row.mean + Z_THRESHOLD * row.std, 2),
            ],
            'z_score': round(row.z, 2),
            'severity': 'high' if abs(row.z) > 3 else 'medium',
        } for row in outliers.itertuples()],
        checked_at=datetime.utcnow().isoformat() + 'Z',
    ), 200


def _count_local_anomalies(region):
    """Cheap in-process anomaly count reused by /trigger-forecast so the
    Power Automate Teams alert can flag issues without a second round-trip."""
    rows = EmploymentData.query.filter_by(RegionName=region).all()
    if len(rows) < 3:
        return 0
    df = pd.DataFrame([{
        'OccupationType': r.OccupationType,
        'EmploymentPercentage': r.EmploymentPercentage,
    } for r in rows])
    grouped = df.groupby('OccupationType')['EmploymentPercentage']
    mean = grouped.transform('mean')
    std = grouped.transform('std').fillna(0.0).replace(0.0, pd.NA)
    z = (df['EmploymentPercentage'] - mean) / std
    return int(z.abs().gt(Z_THRESHOLD).sum())
