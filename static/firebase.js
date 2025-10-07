import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// ✅ Corrected Firebase Config
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

// ✅ Initialize Firebase & Firestore Correctly
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db, collection, addDoc };