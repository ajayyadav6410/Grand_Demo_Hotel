
from database import get_db_connection


def is_room_available(room_id, check_in, check_out):
    """
    Check whether a room is available for the selected dates.
    Existing bookings with Pending or Confirmed status block the room.
    """

    connection = get_db_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM bookings
            WHERE room_id = ?
              AND booking_status IN ('Pending', 'Confirmed')
              AND check_in < ?
              AND check_out > ?
            """,
            (room_id, check_out, check_in)
        ).fetchone()

        return result[0] == 0

    finally:
        connection.close()
