import { Token } from '@lumino/coreutils';

export interface IEnvEntry {
  value: string;
  spawner_value: string | null;
  set_by: string;
  set_at: string;
}

export interface IEnvSync {
  setVar(extensionId: string, key: string, value: string): Promise<void>;
  resetVar(extensionId: string, key: string, force?: boolean): Promise<void>;
  getAll(): Promise<Record<string, IEnvEntry>>;
  getByExtension(extensionId: string): Promise<Record<string, string>>;
  resetAllByExtension(extensionId: string): Promise<void>;
}

export const IEnvSync = new Token<IEnvSync>('jupyterlab-env-sync:IEnvSync');
