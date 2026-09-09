from datetime import datetime, timedelta


def parse_date_range(request):
    today = datetime.now().date()
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')

    try:
        end = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else today
    except ValueError:
        return None, {'detail': 'Invalid date_to format. Use YYYY-MM-DD.'}

    if date_from:
        try:
            start = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            return None, {'detail': 'Invalid date_from format. Use YYYY-MM-DD.'}
    else:
        start = end - timedelta(days=29)

    if start > end:
        return None, {'detail': 'date_from cannot be after date_to.'}

    return (start, end), None