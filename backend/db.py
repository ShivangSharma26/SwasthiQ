import json
from datetime import datetime, timedelta

class ClinicDB:
    def __init__(self, data_path="../clinic.json"):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
            
    def get_patient(self, name=None, phone=None):
        results = []
        for p in self.data["patients"]:
            match = True
            if name and name.lower() not in p["name"].lower():
                match = False
            if phone and p["phone"] != phone:
                match = False
            if match and (name or phone):
                results.append(p)
        return results

    def get_doctor_by_id(self, doc_id):
        for d in self.data["doctors"]:
            if d["id"] == doc_id:
                return d
        return None

    def search_slots(self, doctor_id, date):
        doc = self.get_doctor_by_id(doctor_id)
        if not doc:
            return {"error": "Doctor not found"}
        
        if date in doc.get("leave_dates", []) or date in self.data.get("holidays", []):
            return {"slots": []}
            
        dt = datetime.strptime(date, "%Y-%m-%d")
        day_str = dt.strftime("%a")
        
        # Collect all windows for this day
        windows = [w for w in doc["windows"] if w["day"] == day_str]
        
        all_slots = []
        slot_mins = self.data["clinic"]["slot_minutes"]
        for w in windows:
            start = datetime.strptime(w["start"], "%H:%M")
            end = datetime.strptime(w["end"], "%H:%M")
            curr = start
            while curr + timedelta(minutes=slot_mins) <= end:
                all_slots.append(curr.strftime("%H:%M"))
                curr += timedelta(minutes=slot_mins)
                
        # Remove booked slots
        booked = []
        for app in self.data["appointments"]:
            if app["doctor_id"] == doctor_id and app["date"] == date and app["status"] == "booked":
                booked.append(app["start"])
                
        available = [s for s in all_slots if s not in booked]
        return {"slots": available}
        
    def book_appointment(self, patient_id, doctor_id, date, start_time):
        # Validate patient
        if not any(p["id"] == patient_id for p in self.data["patients"]):
            return {"error": "Patient not found"}
            
        # Validate slot availability
        slots = self.search_slots(doctor_id, date)
        if "error" in slots:
            return slots
        if start_time not in slots["slots"]:
            return {"error": "Slot unavailable"}
            
        # Create appointment
        slot_mins = self.data["clinic"]["slot_minutes"]
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_time = (start_dt + timedelta(minutes=slot_mins)).strftime("%H:%M")
        
        new_id = f"ap_{len(self.data['appointments']) + 1:04d}"
        app = {
            "id": new_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "date": date,
            "start": start_time,
            "end": end_time,
            "status": "booked"
        }
        self.data["appointments"].append(app)
        return app
        
    def reschedule_appointment(self, appointment_id, date, start_time):
        app = None
        for a in self.data["appointments"]:
            if a["id"] == appointment_id and a["status"] == "booked":
                app = a
                break
        if not app:
            return {"error": "Appointment not found or not active"}
            
        # Temporarily remove to check slots
        app["status"] = "rescheduling"
        slots = self.search_slots(app["doctor_id"], date)
        if "error" in slots or start_time not in slots["slots"]:
            app["status"] = "booked"
            return {"error": "Slot unavailable"}
            
        app["status"] = "booked"
        app["date"] = date
        app["start"] = start_time
        slot_mins = self.data["clinic"]["slot_minutes"]
        app["end"] = (datetime.strptime(start_time, "%H:%M") + timedelta(minutes=slot_mins)).strftime("%H:%M")
        return app

    def cancel_appointment(self, appointment_id):
        app = None
        for a in self.data["appointments"]:
            if a["id"] == appointment_id:
                a["status"] = "cancelled"
                app = a
                break
        if not app:
            return {"error": "Appointment not found"}
        return {"status": "success", "appointment": app}
