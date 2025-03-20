export function useConsoleLog() {
  const log = (...args) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(...args);
    }
  };

  const error = (...args) => {
    if (process.env.NODE_ENV === 'development') {
      console.error(...args);
    }
  };

  return { log, error };
}
