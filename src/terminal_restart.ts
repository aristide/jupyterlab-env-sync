import { ServiceManager } from '@jupyterlab/services';
import { Notification } from '@jupyterlab/apputils';

export async function restartTerminals(
  serviceManager: ServiceManager.IManager
): Promise<void> {
  const terminalManager = serviceManager.terminals;

  if (!terminalManager.isReady) {
    await terminalManager.ready;
  }

  const running = Array.from(terminalManager.running());
  if (running.length === 0) {
    return;
  }

  Notification.info(
    `Restarting ${running.length} terminal(s) to apply environment variable changes.`
  );

  const names = running.map(t => t.name);

  for (const name of names) {
    try {
      await terminalManager.shutdown(name);
    } catch (err) {
      console.error(
        `jupyterlab-env-sync: failed to shutdown terminal ${name}:`,
        err
      );
    }
  }

  for (let i = 0; i < names.length; i++) {
    try {
      await terminalManager.startNew();
    } catch (err) {
      console.error('jupyterlab-env-sync: failed to start new terminal:', err);
    }
  }
}
