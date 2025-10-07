// Import Firebase modules (for Firebase v9+)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyB1wJuoTSv6-biDNkaHCpLmxfP26EgpryI",
    authDomain: "doctorpatientvideocall-f3747.firebaseapp.com",
    databaseURL: "https://doctorpatientvideocall-f3747-default-rtdb.firebaseio.com",
    projectId: "doctorpatientvideocall-f3747",
    storageBucket: "doctorpatientvideocall-f3747.firebasestorage.app",
    messagingSenderId: "632543701785",
    appId: "1:632543701785:web:0d5732d0a7e20c35237388",
    measurementId: "G-5T855NQX3K"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Sign Up Function
function signUp() {
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            alert("Signup Successful!");
            console.log(userCredential.user);
            window.location.href="/home"
        })
        .catch((error) => {
            alert(error.message);
        });
}

// Login Function
function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            alert("Login Successful!");
            console.log(userCredential.user);

            // 🔹 Get Firebase ID token
            userCredential.user.getIdToken().then((idToken) => {
                // 🔹 Send token to Flask backend
                fetch("/session_login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ idToken: idToken })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = "/home"; // Redirect after successful session login
                    } else {
                        alert("Session setup failed!");
                    }
                })
                .catch(error => {
                    console.error("Error during session setup:", error);
                });
            });
        })
        .catch((error) => {
            alert(error.message);
        });
}


// Logout Function
function logout() {
    signOut(auth).then(() => {
        alert("Logged out successfully!");
    }).catch((error) => {
        alert(error.message);
    });
}

// Expose functions to HTML
window.signUp = signUp;
window.login = login;
window.logout = logout;
