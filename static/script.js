const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

const ws = new WebSocket(`ws://${location.host}/chat`);

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    appendMessage(message.sender, message.text);
};

sendButton.addEventListener("click", sendMessage);
userInput.addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    const message = userInput.value;
    if (message.trim() !== "") {
        appendMessage("user", message);
        ws.send(JSON.stringify({ text: message }));
        userInput.value = "";
    }
}

function appendMessage(sender, text) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageElement.innerText = text;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}
