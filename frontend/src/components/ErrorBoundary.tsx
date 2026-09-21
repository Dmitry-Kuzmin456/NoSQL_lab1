import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error(error, info.componentStack);
  }

  render(): ReactNode {
    const { error } = this.state;
    if (!error) {
      return this.props.children;
    }

    return (
      <div className="page page--auth">
        <div className="card auth-card">
          <h1>Что-то сломалось</h1>
          <p className="error">{error.message}</p>
          <p className="muted" style={{ marginTop: 12 }}>
            Обновите страницу. Если повторяется — перезапустите npm run dev.
          </p>
          <button
            type="button"
            className="btn btn--primary btn--wide"
            style={{ marginTop: 16 }}
            onClick={() => window.location.reload()}
          >
            Обновить
          </button>
        </div>
      </div>
    );
  }
}
