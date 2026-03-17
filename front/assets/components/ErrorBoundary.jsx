import React from "react";
import "../styles/ErrorBoundary.css";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
    this.handleReset = this.handleReset.bind(this);
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught an error:", error, info.componentStack);
  }

  handleReset() {
    this.setState({ hasError: false });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary d-flex flex-column align-items-center justify-content-center min-vh-100 text-center px-3">
          <div className="error-boundary__box">
            <div className="error-boundary__icon">⚠️</div>
            <h1 className="error-boundary__title">Algo salió mal</h1>
            <p className="error-boundary__message">
              Ocurrió un error inesperado. Puedes intentar de nuevo o volver al
              inicio.
            </p>
            <div className="d-flex gap-3 justify-content-center mt-4">
              <button
                className="btn btn-outline-secondary"
                onClick={this.handleReset}
              >
                Reintentar
              </button>
              <button
                className="btn btn-naranja fw-semibold"
                onClick={() => window.location.replace("/")}
              >
                Volver al inicio
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
