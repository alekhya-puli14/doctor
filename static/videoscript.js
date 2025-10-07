import { db } from "./firebase.js";
import { collection, addDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ script.js is loaded!");

    const button = document.getElementById("makeVideoCallButton");
    const confirmationMessage = document.getElementById("confirmationMessage");

    if (!button) {
        console.error("❌ ERROR: Button not found in the document!");
        return;
    }

    console.log("✅ Button Found!");

    button.addEventListener("click", async () => {
        console.log("✅ Button Clicked!");

        // Prompt user for Room ID
        let roomId = prompt("Enter a Room ID to create:");
        if (!roomId) {
            alert("❌ Room ID cannot be empty!");
            return;
        }

        // Sanitize Room ID
        roomId = roomId.trim().replace(/[^a-zA-Z0-9-_]/g, "");

        if (roomId.length < 3 || roomId.length > 20) {
            alert("❌ Room ID must be between 3-20 characters.");
            return;
        }

        console.log("✅ Room ID Entered:", roomId);

        // Flask-based meeting link
        const meetingLink = `${window.location.origin}/videocall/${roomId}`;

        try {
            // Save Room ID and meeting link to Firestore
            const docRef = await addDoc(collection(db, "appointments"), {
                roomId,
                link: meetingLink,
                timestamp: new Date(),
            });

            console.log("✅ Room Saved to Firestore:", docRef.id);

            // Display confirmation message with meeting link
            confirmationMessage.innerHTML = `
                ✅ Room Created! <br>
                🔗 Your meeting link: <a href="${meetingLink}" target="_blank">${meetingLink}</a>
            `;

            // Redirect user to the video call page
            window.location.href = meetingLink;

        } catch (error) {
            console.error("❌ Error creating room:", error);
            alert("Failed to create the video call room. Check console for details.");
        }
    });
});
