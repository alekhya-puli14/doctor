const doctorsData = {
    pneumonia: [
        { name: "Dr. Rajesh Kumar", contact: "9876543210", clinic: "Apollo Hospital, Chennai", profile: "MD, Pulmonology - AIIMS" },
        { name: "Dr. Sneha Mehta", contact: "9876512345", clinic: "Fortis Hospital, Delhi", profile: "MBBS, MD - Respiratory Medicine" },
        { name: "Dr. Arvind Rao", contact: "9988776655", clinic: "KIMS Hospital, Hyderabad", profile: "DM - Pulmonary Medicine, JIPMER" },
        { name: "Dr. Neha Sharma", contact: "8765432109", clinic: "Medanta, Gurgaon", profile: "DNB - Respiratory Diseases" },
        { name: "Dr. Prakash Iyer", contact: "7654321098", clinic: "CMC Vellore", profile: "MD - Internal Medicine, Pulmonology" }
    ],
    tuberculosis: [
        { name: "Dr. Vishal Nair", contact: "9000001234", clinic: "Apollo Hospital, Mumbai", profile: "MD - Pulmonary TB" },
        { name: "Dr. Ananya Das", contact: "8901234567", clinic: "AIIMS, Delhi", profile: "MBBS, MD - Tuberculosis Specialist" },
        { name: "Dr. Akash Gupta", contact: "8765012345", clinic: "Narayana Hospital, Bangalore", profile: "Pulmonary Medicine, PGI Chandigarh" },
        { name: "Dr. Priya Menon", contact: "7654123789", clinic: "SRM Hospital, Chennai", profile: "DNB - Pulmonary Medicine" },
        { name: "Dr. Rahul Singh", contact: "6543217890", clinic: "Medicare Clinic, Pune", profile: "MD - TB & Chest Diseases" }
    ],
    asthma: [
        { name: "Dr. Karthik Reddy", contact: "9012345678", clinic: "Fortis Hospital, Hyderabad", profile: "Allergy & Asthma Specialist" },
        { name: "Dr. Meera Kapoor", contact: "8123456789", clinic: "Manipal Hospital, Bangalore", profile: "MD - Pulmonary & Respiratory Care" },
        { name: "Dr. Nitin Patel", contact: "7654098765", clinic: "Narayana Hospital, Kolkata", profile: "Respiratory Medicine, AIIMS" }
    ]
};

function showDoctors() {
    let disease = document.getElementById("disease").value;
    let doctorListDiv = document.getElementById("doctorList");

    doctorListDiv.innerHTML = "";

    if (disease && doctorsData[disease]) {
        doctorsData[disease].forEach(doctor => {
            let doctorCard = document.createElement("div");
            doctorCard.classList.add("doctor-card");

            doctorCard.innerHTML = `<h3>${doctor.name}</h3>`;
            doctorCard.onclick = () => {
                window.location.href = `/profile?name=${encodeURIComponent(doctor.name)}&contact=${encodeURIComponent(doctor.contact)}&clinic=${encodeURIComponent(doctor.clinic)}&profile=${encodeURIComponent(doctor.profile)}&disease=${disease}`;
            };            

            doctorListDiv.appendChild(doctorCard);
        });
    }
}
