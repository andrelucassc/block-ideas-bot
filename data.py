from datetime import datetime
import pytz

def change_tz(utc_datetime):
    # Solves TZ implementation of the message
        local_tz = pytz.timezone("America/Sao_Paulo")
        local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        created_at = str(local_datetime.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        return created_at
