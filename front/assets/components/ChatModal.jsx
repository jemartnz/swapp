import React, { useEffect, useMemo, useState } from "react";
import "../styles/ChatModal.css";
import { env } from "../../environ";

/**
 * Props:
 *  - show: boolean
 *  - close: () => void
 *  - receiverId?: number  // (optional) to open chat directly with that user
 */
export default function ChatModal({ show, close, receiverId }) {
  const [me, setMe] = useState(null); // authenticated user
  const [received, setReceived] = useState([]); // messages where I am receiver
  const [sent, setSent] = useState([]); // messages where I am sender
  const [selected, setSelected] = useState(null); // id of the other user
  const [text, setText] = useState("");
  // global name map
  const [names, setNames] = useState(new Map());
  const nameOf = (id) => names.get(id) || `Usuario ${id}`;

  // 1) Load authenticated user
  useEffect(() => {
    if (!show) return;
    const raw = localStorage.getItem("token");
    if (!raw) return;

    const token = raw.replace(/^"|"$/g, "");
    fetch(`${env.api}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setMe)
      .catch(console.error);
  }, [show]);

  // 2) Load messages (when I have my id)
  useEffect(() => {
    if (!me?.id) return;

    const load = async () => {
      try {
        const [r1, r2] = await Promise.all([
          fetch(`${env.api}/api/messages/${me.id}/received`),
          fetch(`${env.api}/api/messages/${me.id}/sent`),
        ]);

        const rec = await r1.json();
        const snt = await r2.json();

        // --- fetch users ---
        const usersResp = await fetch(`${env.api}/api/users`);
        const users = await usersResp.json();
        const userMap = new Map(
          users.map((u) => [u.id, `${u.first_name} ${u.last_name}`])
        );
        setNames(userMap);

        // add names to messages
        const process = (m) => ({
          ...m,
          sender_name:
            userMap.get(m.sender_id) || `Usuario ${m.sender_id}`,
          receiver_name:
            userMap.get(m.receiver_id) || `Usuario ${m.receiver_id}`,
        });

        setReceived(Array.isArray(rec) ? rec.map(process) : []);
        setSent(Array.isArray(snt) ? snt.map(process) : []);
      } catch (e) {
        console.error("Error cargando mensajes:", e);
      }
    };
    load();
  }, [me?.id]);

  // 3) Unify and group by contact (the other id)
  const { contacts, chatsByContact } = useMemo(() => {
    const all = [...received, ...sent].sort(
      (a, b) => new Date(a.sent_at) - new Date(b.sent_at)
    );
    const map = new Map(); // otherId -> messages[]
    for (const m of all) {
      const otherId =
        m.sender_id === me?.id ? m.receiver_id : m.sender_id;
      if (!map.has(otherId)) map.set(otherId, []);
      map.get(otherId).push(m);
    }
    return {
      contacts: Array.from(map.keys()),
      chatsByContact: map,
    };
  }, [received, sent, me?.id]);

  // 4) If receiverId arrives, preselect it
  useEffect(() => {
    if (receiverId && contacts.includes(receiverId)) {
      setSelected(receiverId);
    } else if (receiverId) {
      // if no history, still select that id to be able to write
      setSelected(receiverId);
    }
  }, [receiverId, contacts]);

  if (!show) return null;
  if (!me) return null;

  const currentChat = selected
    ? chatsByContact.get(selected) || []
    : [];

  // 5) Send
  const onSend = async (e) => {
    e.preventDefault();
    const content = text.trim();
    if (!content || !selected || !me?.id) return;

    const body = {
      content,
      sender_id: Number(me.id),
      receiver_id: Number(selected),
    };

    try {
      const res = await fetch(`${env.api}/api/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("No se pudo enviar");
      const newMsg = await res.json();

      // reflect in UI
      setSent((prev) => [
        ...prev,
        {
          ...newMsg,
          sender_name: nameOf(me.id),
          receiver_name: nameOf(selected),
        },
      ]);

      setText("");
    } catch (err) {
      console.error(err);
      alert("No se pudo enviar el mensaje.");
    }
  };

  return (
    <div
      className="modal fade show d-block fondo-modal modal-mensajeria"
      tabIndex="-1"
      role="dialog"
      aria-modal="true"
    >
      <div
        className="modal-dialog modal-xl modal-dialog-centered"
        role="document"
      >
        <div className="modal-content">
          {/* HEADER */}
          <div className="modal-header bg-naranja text-white">
            <h5 className="modal-title">
              Mensajes de {me.first_name} {me.last_name}
            </h5>
            <button
              type="button"
              className="btn-close btn-close-white"
              onClick={close}
            />
          </div>

          {/* BODY */}
          <div className="modal-body fondo-claro">
            <div className="row g-0">
              {/* CONTACT LIST */}
              <div className="col-md-4 border-end bg-white lista-mensajes">
                {contacts.length === 0 && !receiverId ? (
                  <p className="text-center text-muted mt-3">
                    No hay conversaciones todavía.
                  </p>
                ) : (
                  <>
                    {receiverId && !contacts.includes(receiverId) && (
                      <div
                        className={`mensaje-item p-3 border-bottom ${
                          selected === receiverId ? "activo" : ""
                        }`}
                        onClick={() => setSelected(receiverId)}
                      >
                        <strong>{nameOf(receiverId)}</strong>

                        <div className="text-muted small">Nuevo mensaje…</div>
                      </div>
                    )}
                    {contacts.map((id) => {
                      const ms = chatsByContact.get(id) || [];
                      const last = ms[ms.length - 1];
                      return (
                        <div
                          key={id}
                          className={`mensaje-item p-3 border-bottom ${
                            selected === id ? "activo" : ""
                          }`}
                          onClick={() => setSelected(id)}
                        >
                          <div className="d-flex justify-content-between">
                            <div>
                              <strong>
                                {last?.sender_id === me.id
                                  ? `A: ${nameOf(id)}`
                                  : `De: ${nameOf(id)}`}
                              </strong>
                              <div className="text-muted small">
                                {last?.content
                                  ? `${last.content.slice(0, 28)}…`
                                  : ""}
                              </div>
                            </div>
                            <small className="text-muted">
                              {last?.sent_at
                                ? new Date(
                                    last.sent_at
                                  ).toLocaleDateString("es-ES")
                                : ""}
                            </small>
                          </div>
                        </div>
                      );
                    })}
                  </>
                )}
              </div>

              {/* CHAT */}
              <div className="col-md-8 bg-white d-flex flex-column detalle-mensaje">
                <div className="p-3 flex-grow-1 texto-mensaje">
                  {!selected ? (
                    <p className="text-center text-muted mt-5">
                      Selecciona un contacto para chatear.
                    </p>
                  ) : currentChat.length === 0 ? (
                    <p className="text-center text-muted mt-5">
                      Aún no hay mensajes. ¡Escribe el primero!
                    </p>
                  ) : (
                    currentChat.map((m) => (
                      <div
                        key={m.id}
                        className={`mb-2 d-flex ${
                          m.sender_id === me.id
                            ? "justify-content-end"
                            : "justify-content-start"
                        }`}
                      >
                        <div
                          className={
                            m.sender_id === me.id
                              ? "mensaje-enviado"
                              : "mensaje-recibido"
                          }
                        >
                          <p className="mb-1">{m.content}</p>
                          <small className="text-muted">
                            {new Date(m.sent_at).toLocaleTimeString(
                              "es-ES",
                              {
                                hour: "2-digit",
                                minute: "2-digit",
                              }
                            )}
                          </small>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* SEND */}
                {selected && (
                  <form className="p-3 border-top" onSubmit={onSend}>
                    <div className="mb-2">
                      <textarea
                        className="form-control"
                        rows="2"
                        placeholder="Escribe tu mensaje..."
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                      />
                    </div>
                    <div className="text-end">
                      <button
                        type="submit"
                        className="btn btn-naranja fw-semibold"
                      >
                        📤 Enviar mensaje
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
