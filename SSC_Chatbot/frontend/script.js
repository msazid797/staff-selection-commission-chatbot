// ================================================
// CONFIGURATION
// ================================================

const API_URL = "/chat";


// ================================================
// HTML ELEMENTS
// ================================================

const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");

const messages = document.getElementById("messages");
const chatContainer = document.getElementById("chatContainer");

const welcomeScreen = document.getElementById("welcomeScreen");

const chatHistory = document.getElementById("chatHistory");

const newChatButton = document.getElementById("newChatButton");

const clearHistoryButton =
    document.getElementById("clearHistoryButton");

const examSelect = document.getElementById("examSelect");

const menuButton = document.getElementById("menuButton");

const sidebar = document.getElementById("sidebar");


// ================================================
// CHAT STATE
// ================================================

let conversations =
    JSON.parse(localStorage.getItem("sscConversations")) || [];

let currentConversationId = null;


// ================================================
// SAVE HISTORY
// ================================================

function saveConversations() {

    localStorage.setItem(
        "sscConversations",
        JSON.stringify(conversations)
    );
}


// ================================================
// CREATE NEW CHAT
// ================================================

function createNewChat() {

    currentConversationId = null;

    messages.innerHTML = "";

    welcomeScreen.style.display = "block";

    questionInput.value = "";

    examSelect.value = "";

    renderHistory();

    questionInput.focus();
}


// ================================================
// CREATE CONVERSATION
// ================================================

function createConversation(firstQuestion) {

    const conversation = {

        id: Date.now(),

        title: createTitle(firstQuestion),

        messages: []
    };

    conversations.unshift(conversation);

    currentConversationId = conversation.id;

    saveConversations();

    renderHistory();

    return conversation;
}


// ================================================
// CREATE CHAT TITLE
// ================================================

function createTitle(question) {

    const maximumLength = 35;

    if (question.length <= maximumLength) {
        return question;
    }

    return question.substring(0, maximumLength) + "...";
}


// ================================================
// GET CURRENT CONVERSATION
// ================================================

function getCurrentConversation() {

    return conversations.find(
        conversation =>
            conversation.id === currentConversationId
    );
}


// ================================================
// SEND QUESTION
// ================================================

async function sendQuestion(customQuestion = null) {

    const question =
        customQuestion || questionInput.value.trim();

    if (!question) {
        return;
    }


    // Get selected examination

    const selectedExam = examSelect.value;


    // Create a new conversation if required

    let conversation = getCurrentConversation();

    if (!conversation) {

        conversation = createConversation(question);
    }


    // Hide welcome screen

    welcomeScreen.style.display = "none";


    // Add user message

    conversation.messages.push({

        role: "user",

        content: question
    });


    displayMessage(
        "user",
        question
    );


    questionInput.value = "";

    saveConversations();

    renderHistory();


    // Disable button while waiting

    sendButton.disabled = true;


    // Show loading

    const loadingElement = showLoading();


    try {

        let finalQuestion = question;


        // Add selected exam as context

        if (selectedExam) {

            finalQuestion =
                `SSC ${selectedExam}: ${question}`;
        }


        // Send question to FastAPI

        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: finalQuestion
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                "Unable to get response from chatbot."
            );
        }


        const data = await response.json();


        loadingElement.remove();


        // Add assistant response

        conversation.messages.push({

            role: "assistant",

            content: data.answer
        });


        displayMessage(
            "assistant",
            data.answer
        );


        saveConversations();

    }

    catch (error) {

        loadingElement.remove();


        const errorMessage =
            "Sorry, I am unable to process your question right now. Please try again.";


        conversation.messages.push({

            role: "assistant",

            content: errorMessage
        });


        displayMessage(
            "assistant",
            errorMessage
        );


        saveConversations();


        console.error(error);
    }

    finally {

        sendButton.disabled = false;

        questionInput.focus();
    }
}


// ================================================
// DISPLAY MESSAGE
// ================================================

function displayMessage(role, content) {

    const message = document.createElement("div");

    message.classList.add("message");


    if (role === "user") {

        message.innerHTML = `

            <div class="user-message">

                <div class="message-label">
                    You
                </div>

                <div class="message-content"></div>

            </div>
        `;

    }

    else {

        message.innerHTML = `

            <div class="bot-message">

                <div class="message-label">
                    SSC Assistant
                </div>

                <div class="message-content"></div>

                <button class="copy-button">
                    Copy
                </button>

            </div>
        `;
    }


    const contentElement =
        message.querySelector(".message-content");

    contentElement.textContent = content;


    // Copy button

    const copyButton =
        message.querySelector(".copy-button");


    if (copyButton) {

        copyButton.addEventListener(
            "click",
            async () => {

                await navigator.clipboard.writeText(content);

                copyButton.textContent = "Copied";

                setTimeout(
                    () => {
                        copyButton.textContent = "Copy";
                    },
                    1500
                );
            }
        );
    }


    messages.appendChild(message);


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// ================================================
// SHOW LOADING
// ================================================

function showLoading() {

    const loading = document.createElement("div");

    loading.className = "loading";

    loading.textContent =
        "SSC Assistant is thinking...";


    messages.appendChild(loading);


    chatContainer.scrollTop =
        chatContainer.scrollHeight;


    return loading;
}


// ================================================
// RENDER CHAT HISTORY
// ================================================

function renderHistory() {

    chatHistory.innerHTML = "";


    conversations.forEach(conversation => {

        const item =
            document.createElement("div");


        item.className = "history-item";


        if (
            conversation.id ===
            currentConversationId
        ) {

            item.classList.add("active");
        }


        const title =
            document.createElement("div");


        title.className = "history-text";

        title.textContent =
            conversation.title;


        title.addEventListener(
            "click",
            () => {

                loadConversation(
                    conversation.id
                );
            }
        );


        const deleteButton =
            document.createElement("button");


        deleteButton.className =
            "delete-chat";


        deleteButton.textContent = "×";


        deleteButton.title =
            "Delete chat";


        deleteButton.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                deleteConversation(
                    conversation.id
                );
            }
        );


        item.appendChild(title);

        item.appendChild(deleteButton);


        chatHistory.appendChild(item);
    });
}


// ================================================
// LOAD OLD CONVERSATION
// ================================================

function loadConversation(id) {

    const conversation =
        conversations.find(
            conversation =>
                conversation.id === id
        );


    if (!conversation) {
        return;
    }


    currentConversationId = id;


    welcomeScreen.style.display = "none";

    messages.innerHTML = "";


    conversation.messages.forEach(
        message => {

            displayMessage(
                message.role,
                message.content
            );
        }
    );


    renderHistory();


    // Close sidebar on mobile

    sidebar.classList.remove("open");
}


// ================================================
// DELETE ONE CHAT
// ================================================

function deleteConversation(id) {

    conversations =
        conversations.filter(
            conversation =>
                conversation.id !== id
        );


    saveConversations();


    if (currentConversationId === id) {

        createNewChat();

    }

    else {

        renderHistory();
    }
}


// ================================================
// CLEAR ALL HISTORY
// ================================================

function clearAllHistory() {

    const confirmed = confirm(
        "Do you want to delete all chat history?"
    );


    if (!confirmed) {
        return;
    }


    conversations = [];

    saveConversations();

    createNewChat();
}


// ================================================
// SEND BUTTON
// ================================================

sendButton.addEventListener(
    "click",
    () => {

        sendQuestion();
    }
);


// ================================================
// ENTER TO SEND
// SHIFT + ENTER = NEW LINE
// ================================================

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendQuestion();
        }
    }
);


// ================================================
// NEW CHAT BUTTON
// ================================================

newChatButton.addEventListener(
    "click",
    createNewChat
);


// ================================================
// CLEAR HISTORY BUTTON
// ================================================

clearHistoryButton.addEventListener(
    "click",
    clearAllHistory
);


// ================================================
// SUGGESTED QUESTIONS
// ================================================

document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const question =
                    button.dataset.question;

                sendQuestion(question);
            }
        );
    });


// ================================================
// MOBILE SIDEBAR
// ================================================

menuButton.addEventListener(
    "click",
    () => {

        sidebar.classList.toggle("open");
    }
);


// ================================================
// INITIALIZE
// ================================================

renderHistory();

createNewChat();