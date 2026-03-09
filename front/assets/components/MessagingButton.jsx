import "../styles/MessagingButton.css";

export default function MessagingButton({ onClick }) {
  return (
    <button onClick={onClick} className="boton-mensajeria fw-semibold">
      💬 Mensajes
    </button>
  );
}
