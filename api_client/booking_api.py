from api_client.base_client import BaseClient


class BookingAPI(BaseClient):

    def get_bookings(self, params=None, **kwargs):
        return self.get("/booking", params=params, **kwargs)

    def get_booking(self, booking_id: int, **kwargs):
        return self.get(f"/booking/{booking_id}", **kwargs)

    def create_booking(self, booking_data: dict, **kwargs):
        return self.post("/booking", json=booking_data, **kwargs)

    def update_booking(self, booking_id: int, booking_data: dict, token: str, **kwargs):
        return self.put(
            f"/booking/{booking_id}",
            json=booking_data,
            headers={"Cookie": f"token={token}"},
            **kwargs
        )

    def partial_update_booking(self, booking_id: int, booking_data: dict, token: str, **kwargs):
        return self.patch(
            f"/booking/{booking_id}",
            json=booking_data,
            headers={"Cookie": f"token={token}"},
            **kwargs
        )

    def delete_booking(self, booking_id: int, token: str, **kwargs):
        return self.delete(
            f"/booking/{booking_id}",
            headers={"Cookie": f"token={token}"},
            **kwargs
        )
