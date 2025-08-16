from io import BytesIO


def test_import_data(app, client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN a CSV file is uploaded via the '/datatable' endpoint
    THEN ensure the upload is processed successfully
    """
    # ARRANGE: Disable CSRF and prepare mock CSV data
    app.config['WTF_CSRF_ENABLED'] = False
    data = {
        'file': (BytesIO(
            b'Region,Year,Gender,Occupation Type,Percentage Employed '
            b'(Relative to Total Employment in the Year),Margin of Error '
            b'(%),Latitude,Longitude\n'
            b'TestRegion,2025,Female,TestOccupation,50.0,5.0,40.7128,-74.0060'
        ), 'test.csv'),
        'submit': 'Upload File'
    }

    # ACT: Simulate file upload
    response = client.post(
        '/datatable', data=data, content_type='multipart/form-data',
        follow_redirects=True
    )

    # ASSERT: Verify the response status code
    assert response.status_code == 200


def test_export_csv(client):
    """
    GIVEN a Flask application with data available for export
    WHEN the '/datatable' endpoint is accessed with 'export=csv'
    THEN ensure a CSV file is returned with the correct content
    """
    # ARRANGE: No specific setup required

    # ACT: Request CSV export
    response = client.get('/datatable?export=csv')

    # ASSERT: Verify the response status and content
    assert response.status_code == 200
    assert response.content_type == 'text/csv; charset=utf-8'
    assert b'Region' in response.data
    assert b'Year' in response.data
    assert b'OccupationType' in response.data


def test_export_xlsx(client):
    """
    GIVEN a Flask application with data available for export
    WHEN the '/datatable' endpoint is accessed with 'export=xlsx'
    THEN ensure an XLSX file is returned with the correct content
    """
    # ARRANGE: No specific setup required

    # ACT: Request XLSX export
    response = client.get('/datatable?export=xlsx')

    # ASSERT: Verify the response status and content type
    assert response.status_code == 200
    assert response.content_type == (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
