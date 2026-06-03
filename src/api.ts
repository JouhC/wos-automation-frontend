export type Player = {
  fid: number;
  avatar_image?: string;
  nickname: string;
  stove_lv?: string | number;
  stove_lv_content?: string;
  kid: string | number;
  redeemed_all: number | boolean | string;
};

export type ApiResponse<T> = T & { error?: string };

const apiBase = import.meta.env.VITE_API_URL || import.meta.env.URL || window.location.origin;

async function safeFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${apiBase}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }

  return response.json();
}

function post<T>(path: string, data?: unknown, options: RequestInit = {}): Promise<T> {
  return safeFetch<T>(path, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

export async function listPlayers(): Promise<ApiResponse<{ players: Player[] }>> {
  return safeFetch('/players');
}

export async function listGiftcodes(): Promise<ApiResponse<{ giftcodes: string[] }>> {
  return safeFetch('/giftcodes');
}

export async function createPlayer(playerId: string): Promise<ApiResponse<{ message: string }>> {
  return post('/players/create/', { player_id: playerId });
}

export async function removePlayer(playerId: string, adminPassword: string): Promise<ApiResponse<{ message: string }>> {
  return post('/players/remove/', { player_id: playerId }, {
    headers: {
      'X-Admin-Password': adminPassword,
    },
  });
}

export async function expiredCheck(): Promise<ApiResponse<{ task_id?: string }>> {
  return post('/tasks/expired-check/');
}

export async function runMainLogic(): Promise<ApiResponse<{ task_id?: string }>> {
  return post('/tasks/automate-all/', { n: 'all' });
}

export async function getTaskStatus(taskId: string): Promise<ApiResponse<{ progress?: number; status?: string; error?: string }>> {
  return safeFetch(`/tasks/${taskId}/`);
}

export async function checkInProgress(): Promise<ApiResponse<{ result?: boolean; task_id?: string } | string>> {
  return safeFetch('/tasks/inprogress/');
}
