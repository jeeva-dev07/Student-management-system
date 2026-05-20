const API_URL = 'http://127.0.0.1:5000/api/students';

// Elements - (HTML IDs kooda exact-ah match panniyachu)
const studentForm = document.getElementById('studentForm');
const studentTableBody = document.getElementById('studentTableBody');
const totalCount = document.getElementById('totalCount');
const searchBar = document.getElementById('searchBar');
const cancelBtn = document.getElementById('cancelBtn');
const submitBtn = document.getElementById('submitBtn');
const formTitle = document.getElementById('formTitle');

let isEditing = false;
let editStudentId = null;

// Fetch and Render Students
async function fetchStudents() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Failed to fetch data');
        const students = await response.json();
        renderStudents(students);
    } catch (error) {
        console.error('Error:', error);
    }
}

function renderStudents(students) {
    studentTableBody.innerHTML = '';
    totalCount.textContent = students.length;

    students.forEach(student => {
        const tr = document.createElement('tr');
        
        // Object-ah string format-ku safe-ah mathuroom quotes break aagama iruka
        const studentStr = encodeURIComponent(JSON.stringify(student));
        
        tr.innerHTML = `
            <td>${student.full_name}</td>
            <td>${student.email}</td>
            <td>${student.phone}</td>
            <td>${student.course}</td>
            <td>${student.enrolled_on}</td>
            <td>
                <button class="btn btn-primary btn-inline" onclick="editStudent('${studentStr}')">Edit</button>
                <button class="btn btn-danger btn-inline" onclick="deleteStudent(${student.id})">Delete</button>
            </td>
        `;
        studentTableBody.appendChild(tr);
    });
}

// Handle Submit (Insert / Update)
studentForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const studentData = {
        full_name: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        course: document.getElementById('course').value
    };

    try {
        let response;
        if (isEditing) {
            response = await fetch(`${API_URL}/${editStudentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(studentData)
            });
        } else {
            response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(studentData)
            });
        }

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            resetForm();
            fetchStudents();
        } else {
            alert(result.error || 'Something went wrong');
        }
    } catch (error) {
        console.error('Error handling submit:', error);
        alert('Could not connect to backend server');
    }
});

// Edit Student Profile Setup
window.editStudent = function(studentStrEncoded) {
    // Encoded string-ah thirumba normal object-ah mathuroom
    const student = JSON.parse(decodeURIComponent(studentStrEncoded));

    isEditing = true;
    editStudentId = student.id;
    
    document.getElementById('fullName').value = student.full_name;
    document.getElementById('email').value = student.email;
    document.getElementById('phone').value = student.phone;
    document.getElementById('course').value = student.course;
    
    // UI state change for editing
    formTitle.textContent = 'Edit Student Details';
    submitBtn.textContent = 'Update Student Details';
    cancelBtn.classList.remove('hidden');
};

// Cancel Button Mechanism
cancelBtn.addEventListener('click', () => {
    resetForm();
});

// Delete Student Record
window.deleteStudent = async function(id) {
    if (confirm('Are you sure you want to remove this student profile?')) {
        try {
            const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchStudents();
            } else {
                alert(result.error);
            }
        } catch (error) {
            console.error('Error deleting record:', error);
        }
    }
};

// Live Search Filter
searchBar.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const results = await response.json();
            renderStudents(results);
        }
    } catch (error) {
        console.error('Search error:', error);
    }
});

function resetForm() {
    studentForm.reset();
    isEditing = false;
    editStudentId = null;
    formTitle.textContent = 'Add New Student';
    submitBtn.textContent = 'Save Student';
    cancelBtn.classList.add('hidden');
}

// Start Initialization
fetchStudents();
