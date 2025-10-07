import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// 🔹 Initialize Firebase (Make sure this matches your `script.js` Firebase config)
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

document.addEventListener("DOMContentLoaded", () => {
    const profileButton = document.getElementById("profile-button");
    const profilePic = document.getElementById("profile-pic");

    if (!profileButton || !profilePic) {
        console.error("Profile button or profile image not found!");
        return;
    }

    onAuthStateChanged(auth, (user) => {
        if (user) {
            console.log("User is logged in:", user.email);

            // Update profile picture if available
            if (user.photoURL) {
                profilePic.src = user.photoURL;
            }

            // Ensure the button redirects to dashboard
            profileButton.addEventListener("click", () => {
                console.log("Redirecting to dashboard...");
                window.location.href = "/dashboard";
            });

        } else {
            console.warn("No user logged in! Redirecting to login page...");
            window.location.href = "/"; // Redirect to login page if no user
        }
    });
});
