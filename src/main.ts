import {
  checkInProgress,
  createPlayer,
  expiredCheck,
  getTaskStatus,
  listGiftcodes,
  listPlayers,
  removePlayer,
  runMainLogic,
  type Player,
} from './api';

const elements = {
  newPlayerInput: document.getElementById('newPlayerId') as HTMLInputElement,
  addPlayerBtn: document.getElementById('addPlayerBtn') as HTMLButtonElement,
  removePlayerSelect: document.getElementById('removePlayerSelect') as HTMLSelectElement,
  removePlayerBtn: document.getElementById('removePlayerBtn') as HTMLButtonElement,
  fetchCodesBtn: document.getElementById('fetchCodesBtn') as HTMLButtonElement,
  redeemCodesBtn: document.getElementById('redeemCodesBtn') as HTMLButtonElement,
  refreshBtn: document.getElementById('refreshBtn') as HTMLButtonElement,
  statusText: document.getElementById('statusText') as HTMLDivElement,
  progressBar: document.getElementById('progressBar') as HTMLDivElement,
  playersTableBody: document.querySelector('#playersTable tbody') as HTMLTableSectionElement,
  giftcodesList: document.getElementById('giftcodesList') as HTMLDivElement,
  pageDate: document.getElementById('pageDate') as HTMLSpanElement,
  themeToggle: document.getElementById('themeToggle') as HTMLButtonElement,
};

let activeTaskTimer: number | null = null;

function setStatus(message: string, kind: 'info' | 'success' | 'error' = 'info') {
  elements.statusText.textContent = message;
  elements.statusText.className = `status-text ${kind}`;
}

function setProgress(value: number) {
  elements.progressBar.style.width = `${Math.min(Math.max(value, 0), 100)}%`;
}

function clearProgress() {
  setProgress(0);
}

function setLoading(isLoading: boolean) {
  [
    elements.addPlayerBtn,
    elements.removePlayerBtn,
    elements.fetchCodesBtn,
    elements.redeemCodesBtn,
    elements.refreshBtn,
  ].forEach((button) => {
    if (button) {
      button.disabled = isLoading;
    }
  });
}

function applyTheme(theme: 'dark' | 'light') {
  if (theme === 'dark') {
    document.body.classList.add('dark');
  } else {
    document.body.classList.remove('dark');
  }
  try {
    localStorage.setItem('theme', theme);
  } catch (_) {}
  if (elements.themeToggle) {
    elements.themeToggle.textContent = theme === 'dark' ? 'Switch to Light' : 'Switch to Night';
  }
}

function initTheme() {
  let theme: 'dark' | 'light' = 'dark';
  try {
    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') theme = stored;
  } catch (_) {}
  applyTheme(theme);
}

function toggleTheme() {
  const current = document.body.classList.contains('dark') ? 'dark' : 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

function createPlayerRow(player: Player): HTMLTableRowElement {
  const row = document.createElement('tr');

  const avatarCell = document.createElement('td');
  const avatar = document.createElement('img');
  avatar.className = 'avatar';
  avatar.src = player.avatar_image || 'https://via.placeholder.com/42?text=?';
  avatar.alt = player.nickname;
  avatar.onerror = () => {
    avatar.src = 'https://via.placeholder.com/42?text=?';
  };
  avatarCell.appendChild(avatar);

  const nicknameCell = document.createElement('td');
  nicknameCell.textContent = String(player.nickname);

  const stoveCell = document.createElement('td');
  // Prefer `stove_lv_content` (may include an image + level HTML), fall back to `stove_lv`
  if (player.stove_lv_content) {
    stoveCell.innerHTML = String(player.stove_lv_content);
  } else {
    stoveCell.textContent = String(player.stove_lv ?? '—');
  }

  const kidCell = document.createElement('td');
  kidCell.textContent = String(player.kid ?? '—');

  const redeemedCell = document.createElement('td');
  redeemedCell.textContent = [1, '1', true, 'true'].includes(player.redeemed_all as any) ? '✅' : '❌';

  row.append(avatarCell, nicknameCell, stoveCell, kidCell, redeemedCell);
  return row;
}

function updatePlayersTable(players: Player[]) {
  elements.playersTableBody.innerHTML = '';
  if (!players.length) {
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = '<td colspan="5" class="empty-cell">No subscribed players found.</td>';
    elements.playersTableBody.appendChild(emptyRow);
    return;
  }

  players.forEach((player) => {
    elements.playersTableBody.appendChild(createPlayerRow(player));
  });
}

function updateGiftCodesList(codes: string[]) {
  elements.giftcodesList.innerHTML = '';
  if (!codes.length) {
    elements.giftcodesList.innerHTML = '<p>No gift codes available.</p>';
    return;
  }
  codes.forEach((code) => {
    const codeBlock = document.createElement('div');
    codeBlock.className = 'giftcode';
    codeBlock.textContent = code;
    elements.giftcodesList.appendChild(codeBlock);
  });
}

function updateRemovePlayerOptions(players: Player[]) {
  elements.removePlayerSelect.innerHTML = '<option value="">-- Choose player --</option>';
  players.forEach((player) => {
    const option = document.createElement('option');
    option.value = String(player.fid);
    option.textContent = `${player.nickname} (${player.fid})`;
    elements.removePlayerSelect.appendChild(option);
  });
}

async function refreshData() {
  try {
    setLoading(true);
    setStatus('Loading players and gift codes...');
    clearProgress();

    const [playersResponse, giftcodesResponse] = await Promise.all([listPlayers(), listGiftcodes()]);
    const players = playersResponse.players ?? [];
    const giftcodes = giftcodesResponse.giftcodes ?? [];

    updatePlayersTable(players);
    updateGiftCodesList(giftcodes);
    updateRemovePlayerOptions(players);
    setStatus('Data refreshed successfully.', 'success');
  } catch (error) {
    setStatus(`Unable to load data: ${(error as Error).message}`, 'error');
  } finally {
    setLoading(false);
  }
}

async function handleAddPlayer() {
  const playerId = elements.newPlayerInput.value.trim();
  if (!playerId) {
    setStatus('Player ID cannot be empty.', 'error');
    return;
  }

  try {
    setLoading(true);
    setStatus('Adding player...');
    await createPlayer(playerId);
    elements.newPlayerInput.value = '';
    setStatus('Player added successfully.', 'success');
    await refreshData();
  } catch (error) {
    setStatus(`Failed to add player: ${(error as Error).message}`, 'error');
  } finally {
    setLoading(false);
  }
}

async function handleRemovePlayer() {
  const playerId = elements.removePlayerSelect.value;

  if (!playerId) {
    setStatus('Please select a player to remove.', 'error');
    return;
  }

  try {
    setLoading(true);
    setStatus('Removing player...');
    await removePlayer(playerId);
    setStatus('Player removed successfully.', 'success');
    await refreshData();
  } catch (error) {
    setStatus(`Failed to remove player: ${(error as Error).message}`, 'error');
  } finally {
    setLoading(false);
  }
}

function getTaskIdFromResponse(response: any): string {
  if (!response) {
    throw new Error('Task response was empty.');
  }
  if (typeof response === 'string') {
    return response;
  }
  return response.task_id ?? '';
}

async function trackTask(taskId: string) {
  return new Promise<void>((resolve, reject) => {
    if (!taskId) {
      reject(new Error('Invalid task ID.'));
      return;
    }

    if (activeTaskTimer) {
      window.clearInterval(activeTaskTimer);
      activeTaskTimer = null;
    }

    const poll = async () => {
      try {
        const statusResponse = await getTaskStatus(taskId);
        const progress = statusResponse.progress ?? 0;
        const status = statusResponse.status ?? 'Processing';

        setProgress(progress);
        setStatus(`Progress: ${progress}% - ${status}`);

        if (['Completed', 'Failed', 'Timeout'].includes(status)) {
          if (activeTaskTimer) {
            window.clearInterval(activeTaskTimer);
            activeTaskTimer = null;
          }

          if (status === 'Completed') {
            setProgress(100);
            resolve();
          } else {
            reject(new Error(statusResponse.error ?? `Task ended with status: ${status}`));
          }
        }
      } catch (error) {
        if (activeTaskTimer) {
          window.clearInterval(activeTaskTimer);
          activeTaskTimer = null;
        }
        reject(error);
      }
    };

    poll();
    activeTaskTimer = window.setInterval(poll, 5000);
  });
}

async function performTask(taskType: 'automate-all' | 'expired-check') {
  try {
    setLoading(true);
    setStatus('Checking for active tasks...');
    clearProgress();

    const inProgress = await checkInProgress();
    let taskId = '';

    if (inProgress && typeof inProgress === 'object' && inProgress.result) {
      taskId = String(inProgress.task_id || '');
    }

    if (!taskId) {
      setStatus('Starting task...');
      const response = taskType === 'automate-all' ? await runMainLogic() : await expiredCheck();
      taskId = getTaskIdFromResponse(response);
    }

    setStatus('Task started. Tracking progress...');
    await trackTask(taskId);
    await refreshData();

    setStatus(taskType === 'automate-all' ? 'Gift codes applied successfully.' : 'Gift codes fetched successfully.', 'success');
  } catch (error) {
    setStatus(`Task failed: ${(error as Error).message}`, 'error');
  } finally {
    setLoading(false);
  }
}

function bindEvents() {
  elements.addPlayerBtn.addEventListener('click', handleAddPlayer);
  elements.removePlayerBtn.addEventListener('click', handleRemovePlayer);
  elements.fetchCodesBtn.addEventListener('click', () => performTask('expired-check'));
  elements.redeemCodesBtn.addEventListener('click', () => performTask('automate-all'));
  elements.refreshBtn.addEventListener('click', refreshData);
  if (elements.themeToggle) {
    elements.themeToggle.addEventListener('click', toggleTheme);
  }
}

function initializeDate() {
  const now = new Date();
  const formatted = now.toLocaleDateString(undefined, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
  elements.pageDate.textContent = `Date: ${formatted}`;
}

async function init() {
  initTheme();
  bindEvents();
  initializeDate();
  await refreshData();
}

init().catch((error) => {
  setStatus(`Failed to initialize app: ${(error as Error).message}`, 'error');
});
