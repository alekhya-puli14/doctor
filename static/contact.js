// Import Firebase SDK
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getFirestore, collection, addDoc } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDnk-0WO6-LlD-wWT-5iab8rmTf-oZZu-I",
    authDomain: "contactmessages-d01a7.firebaseapp.com",
    projectId: "contactmessages-d01a7",
    storageBucket: "contactmessages-d01a7.appspot.com", // Fixed incorrect storage bucket
    messagingSenderId: "216011024617",
    appId: "1:216011024617:web:4c100803a9791710972878",
    measurementId: "G-80HGTLGE8S"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Function to submit form data
async function submitForm(event) {
    event.preventDefault(); // Prevent form refresh

    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let message = document.getElementById("message").value;

    if (name && email && message) {
        try {
            const docRef = await addDoc(collection(db, "contactMessages"), {
                name,
                email,
                message,
                timestamp: new Date()
            });
            console.log("Document written with ID: ", docRef.id);
            alert("Message Sent Successfully!");
            document.getElementById("contact-form").reset();
        } catch (error) {
            console.error("Firestore Error:", error.code, error.message);
            alert("Error: " + error.message);
        }
    } else {
        alert("Please fill in all fields.");
    }
}

// Attach event listener
document.getElementById("contact-form").addEventListener("submit", submitForm);
