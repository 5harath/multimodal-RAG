import { useState, useRef, useEffect } from 'react';

function Chatbot() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const newMessage = { role: 'user', content: query };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setLoading(true);
    setQuery('');

    const startTime = Date.now(); // Start timing API call

    try {
      const res = await fetch('http://127.0.0.1:8080/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      const endTime = Date.now(); // End timing API call
      const timeTaken = ((endTime - startTime) / 1000).toFixed(2); // Calculate latency in seconds

      const data = await res.json();

      const botMessage = { 
        role: 'bot', 
        content: data.response || "Sorry, I couldn't get a response.", 
        timeTaken 
      };
      
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('API Error:', error);
      const errorMessage = { 
        role: 'bot', 
        content: "Error: Could not connect to the RAG server.", 
        timeTaken: 'N/A' 
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="title">MultiModal RAG Chatbot</div>
      <div className="chat-container" ref={chatContainerRef}>
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {/* Logic to bold text wrapped in *** */}
            {message.content.split('***').map((part, i) => (
              i % 2 === 1 ? <strong key={i}>{part}</strong> : part
            ))}
            
            {/* Display time taken for bot responses */}
            {message.role === 'bot' && message.timeTaken && (
              <div className="time-taken">Response time: {message.timeTaken}s</div>
            )}
          </div>
        ))}
        
        {loading && (
          <div className="message bot loading">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}
      </div>

      <form className="Input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="Input-box"
          placeholder="Ask a question about your documents..."
          disabled={loading}
        />
        <button type="submit" className="submit-button" disabled={loading}>
          {/* Feather send icon SVG */}
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feather feather-send">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>

      {/* Styled JSX for the UI appearance and animations */}
      <style jsx>{`
        .container {
          display: flex;
          flex-direction: column;
          align-items: center;
          height: 100vh;
          font-family: 'Roboto', sans-serif;
          background-color: #f4f7f6;
          padding: 20px;
        }
        .title {
          font-size: 3rem;
          font-weight: bold;
          color: #333;
          margin-bottom: 20px;
          text-align: center;
        }
        .chat-container {
          width: 100%;
          max-width: 700px;
          height: 600px;
          border: 1px solid #ccc;
          border-radius: 12px;
          padding: 15px;
          overflow-y: scroll;
          display: flex;
          flex-direction: column;
          margin-bottom: 15px;
          background-color: #fff;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .message {
          max-width: 80%;
          padding: 10px 15px;
          border-radius: 18px;
          margin-bottom: 10px;
          line-height: 1.5;
          word-wrap: break-word;
          font-size: 1rem;
          color: #fff;
        }
        .message.user {
          align-self: flex-end;
          background-color: rgb(46, 170, 252);
          border-bottom-right-radius: 4px;
        }
        .message.bot {
          align-self: flex-start;
          background-color: rgb(146, 146, 146);
          border-bottom-left-radius: 4px;
          color: #fff;
        }
        .time-taken {
          font-size: 0.75rem;
          margin-top: 5px;
          color: rgba(255, 255, 255, 0.8);
          font-style: italic;
        }
        .Input-form {
          display: flex;
          width: 100%;
          max-width: 700px;
          gap: 10px;
        }
        .Input-box {
          flex-grow: 1;
          padding: 12px 18px;
          border: 1px solid #ddd;
          border-radius: 25px;
          font-size: 1rem;
          outline: none;
          transition: border-color 0.3s;
        }
        .Input-box:focus {
          border-color: #007bff;
        }
        .submit-button {
          background-color: #007bff;
          color: white;
          border: none;
          padding: 12px 20px;
          border-radius: 25px;
          cursor: pointer;
          transition: background-color 0.3s, transform 0.1s;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .submit-button:hover:not(:disabled) {
          background-color: #005eb3;
        }
        .submit-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        .message.bot.loading {
          display: flex;
          align-items: center;
          background-color: rgb(146, 146, 146);
          padding: 10px 20px;
        }
        .dot {
          width: 8px;
          height: 8px;
          background-color: #fff;
          border-radius: 50%;
          margin: 0 4px;
          animation: blink 1.4s infinite;
          opacity: 0;
        }
        .dot:nth-child(1) {
          animation-delay: 0s;
        }
        .dot:nth-child(2) {
          animation-delay: 0.2s;
        }
        .dot:nth-child(3) {
          animation-delay: 0.4s;
        }
        @keyframes blink {
          0%, 100% {
            opacity: 0;
            transform: scale(0.8);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }
        /* Media Query for smaller screens */
        @media (max-width: 768px) {
          .title {
            font-size: 2rem;
          }
          .chat-container {
            height: 70vh;
            max-width: 100%;
          }
          .Input-form {
            max-width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export default Chatbot;