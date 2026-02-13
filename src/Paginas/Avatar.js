import { useRef, useState } from "react";
import "../Style/Avatar.css"
function AvatarVideo() {
  const videoRef = useRef(null);
  const [hablando, setHablando] = useState(false);

  const hablar = () => {
    const msg = new SpeechSynthesisUtterance(
      "Lo hicimos chicos"
    );
    msg.lang = "es-ES";

    msg.onstart = () => {
      setHablando(true);
      videoRef.current.play();
    };

    msg.onend = () => {
      setHablando(false);
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    };

    window.speechSynthesis.speak(msg);
  };

  return (
    <div style={{ textAlign: "center" }}>
      <video className="video"
        ref={videoRef}
        src="https://cdn.pixabay.com/video/2022/12/11/142558-780232291_large.mp4"
        width="200"
        loop
        muted
      />

      <br />
      <button onClick={hablar}>🎙️ Hablar</button>
    </div>
  );
}

export default AvatarVideo;
