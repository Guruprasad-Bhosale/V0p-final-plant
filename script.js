document.addEventListener('DOMContentLoaded', function() {
    // Simulate loading time
    setTimeout(function() {
        const loader = document.querySelector('.loader');
        if (loader) {
            loader.style.display = 'none';
        }
        document.querySelector('header').style.display = 'block';
        document.querySelector('main').style.display = 'block';
    }, 2000);  // 2 seconds delay

    // Image preview functionality
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const imagePreviewContainer = document.getElementById('image-preview-container');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreviewContainer.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Plant identification functionality
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const loadingDiv = document.getElementById('loading');
            const errorDiv = document.getElementById('error');
            
            loadingDiv.style.display = 'block';
            errorDiv.style.display = 'none';
            
            fetch('/api/identify-plant', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loadingDiv.style.display = 'none';
                if (data.error) {
                    errorDiv.textContent = data.error;
                    errorDiv.style.display = 'block';
                } else {
                    localStorage.setItem('plantData', JSON.stringify(data));
                    window.location.href = '/result';
                }
            })
            .catch(error => {
                loadingDiv.style.display = 'none';
                errorDiv.textContent = 'An error occurred. Please try again.';
                errorDiv.style.display = 'block';
                console.error('Error:', error);
            });
        });
    }

    // Display result
    const resultDiv = document.getElementById('result');
    if (resultDiv) {
        const plantData = JSON.parse(localStorage.getItem('plantData'));
        if (plantData) {
            document.getElementById('plant-image').src = 'data:image/jpeg;base64,' + plantData.images[0];
            document.getElementById('plant-name').textContent = plantData.name;
            document.getElementById('plant-info').textContent = plantData.info || 'No information available.';
            
            // Add placeholder text for medicinal use and meaning
            // In a real application, you would fetch this data from an API or database
            document.getElementById('plant-medicinal-use').textContent = 'Medicinal use information not available.';
            document.getElementById('plant-meaning').textContent = 'Plant meaning information not available.';
        } else {
            resultDiv.innerHTML = '<p>No plant data available. Please scan a plant first.</p>';
        }
    }
});

console.log("PlantPedia App Loaded");