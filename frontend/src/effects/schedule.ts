import { mockSchedule } from "./mockData";

const shouldMock = false;

export async function getSchedule(userId: string) {
  if (shouldMock) return mockSchedule;

  const response = await fetch(
    `${process.env.REACT_APP_BASE_URL}/schedule?user_id=${userId}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw Error("Network response was not ok");
  }

  return await response.json();
}
