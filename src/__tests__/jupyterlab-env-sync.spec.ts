import { buildSnippet } from '../kernel_inject';

describe('buildSnippet', () => {
  describe('python', () => {
    it('should generate set snippet', () => {
      const code = buildSnippet('python', 'FOO', 'bar');
      expect(code).toBe('import os; os.environ["FOO"] = "bar"');
    });

    it('should generate delete snippet', () => {
      const code = buildSnippet('python', 'FOO', null);
      expect(code).toBe('import os; os.environ.pop("FOO", None)');
    });

    it('should escape special characters', () => {
      const code = buildSnippet('python', 'KEY', 'val"ue\\n');
      expect(code).toContain('\\"');
      expect(code).toContain('\\\\');
    });
  });

  describe('r', () => {
    it('should generate set snippet', () => {
      const code = buildSnippet('r', 'DB_URL', 'postgres://localhost');
      expect(code).toBe(
        'Sys.setenv("DB_URL" = "postgres://localhost")'
      );
    });

    it('should generate unset snippet', () => {
      const code = buildSnippet('r', 'DB_URL', null);
      expect(code).toBe('Sys.unsetenv("DB_URL")');
    });
  });

  describe('julia', () => {
    it('should generate set snippet', () => {
      const code = buildSnippet('julia', 'API_KEY', 'secret');
      expect(code).toBe('ENV["API_KEY"] = "secret"');
    });

    it('should generate delete snippet', () => {
      const code = buildSnippet('julia', 'API_KEY', null);
      expect(code).toBe('delete!(ENV, "API_KEY")');
    });
  });

  describe('unsupported language', () => {
    it('should return null', () => {
      const code = buildSnippet('rust', 'KEY', 'val');
      expect(code).toBeNull();
    });
  });
});
