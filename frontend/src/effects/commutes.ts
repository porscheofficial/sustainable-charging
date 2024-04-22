import { CommuteType } from "../models/CommuteType";

export async function addCommute(values: CommuteType) {
  const response = await fetch(`${process.env.REACT_APP_BASE_URL}/commutes`, {
    method: "POST",
    body: JSON.stringify(values),
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw Error("Network response was not ok");
  }

  return await response.json();
}

export async function getCommutes(userId: string) {
  const response = await fetch(
    `${process.env.REACT_APP_BASE_URL}/commutes?user_id=${userId}`,
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
