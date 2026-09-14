// Normalized from data/structured/package_catalog.json; price_status verified_saved_snapshot.
export interface Program {
  id: string;
  title: string;
  detail: string;
  price: number;
  url: string;
}
export const programs: Program[] = [
  {
    id: "teen_24_hr_classroom_driving_package",
    title: "Teen driver education",
    detail: "Classroom + driving package",
    price: 399.0,
    url: "https://bestdrivingschool.us/driving-courses/teen-24-hour-class-room-and-driving-package",
  },
  {
    id: "adult_2_hours",
    title: "Adult driving lessons",
    detail: "2 hours behind the wheel",
    price: 180.0,
    url: "https://bestdrivingschool.us/driving-courses/adult-driving-sessions",
  },
  {
    id: "adult_6_hour_online_permit_class",
    title: "Online permit class",
    detail: "6-hour online course",
    price: 19.99,
    url: "https://bestdrivingschool.us/driving-courses/adult-6-hours-online-permit-class",
  },
  {
    id: "parent_taught_10_hours",
    title: "Parent-taught support",
    detail: "10 hours of log driving",
    price: 450.0,
    url: "https://bestdrivingschool.us/driving-courses/log-driving-hours",
  },
  {
    id: "road_test_road_test_only",
    title: "3rd-party road test",
    detail: "Road test only",
    price: 100.0,
    url: "https://bestdrivingschool.us/driving-courses/road-test",
  },
];
