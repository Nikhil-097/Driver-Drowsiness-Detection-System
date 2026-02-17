gsap.registerPlugin(ScrollTrigger);

let globalParticles = [];

// ================= PARTICLE SYSTEM =================

document.querySelectorAll(".section").forEach(section => {

    const container = section.querySelector(".three-container");

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
        75,
        section.clientWidth / section.clientHeight,
        0.1,
        1000
    );

    const renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setSize(section.clientWidth, section.clientHeight);
    container.appendChild(renderer.domElement);

    camera.position.z = 5;

    const particleCount = 400;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 10;
        positions[i * 3 + 1] = Math.random() * 10;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 5;
    }

    geometry.setAttribute(
        'position',
        new THREE.BufferAttribute(positions, 3)
    );

    const material = new THREE.PointsMaterial({
        color: 0x2E8B57,
        size: 0.05
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    globalParticles.push(material);

    let scrollY = 0;

    window.addEventListener("scroll", () => {
        scrollY = window.scrollY;
    });

    function animate() {
        requestAnimationFrame(animate);

        const pos = particles.geometry.attributes.position;

        for (let i = 0; i < particleCount; i++) {
            pos.array[i * 3 + 1] -= 0.02;
            if (pos.array[i * 3 + 1] < -5) {
                pos.array[i * 3 + 1] = 5;
            }
        }

        pos.needsUpdate = true;

        particles.rotation.y = scrollY * 0.0005;

        renderer.render(scene, camera);
    }

    animate();
});

// ================= GSAP TEXT ANIMATION =================

gsap.utils.toArray(".animate").forEach(element => {

    gsap.fromTo(element,
        { opacity: 0, y: 60 },
        {
            opacity: 1,
            y: 0,
            duration: 1,
            scrollTrigger: {
                trigger: element,
                start: "top 80%",
                toggleActions: "restart none restart none"
            }
        }
    );
});

// ================= REAL-TIME EAR GRAPH =================

const ctx = document.getElementById('earChart').getContext('2d');

const earData = {
    labels: [],
    datasets: [{
        label: 'EAR Value',
        data: [],
        borderColor: '#2E8B57',
        borderWidth: 2,
        fill: false
    }]
};

const earChart = new Chart(ctx, {
    type: 'line',
    data: earData,
    options: {
        animation: false,
        scales: {
            y: { min: 0, max: 0.5 }
        }
    }
});

// Fetch EAR + Drowsy Status
setInterval(() => {
    fetch("/status")
    .then(res => res.json())
    .then(data => {

        if (earData.labels.length > 30) {
            earData.labels.shift();
            earData.datasets[0].data.shift();
        }

        earData.labels.push('');
        earData.datasets[0].data.push(data.ear);
        earChart.update();

        // Particle color change
        globalParticles.forEach(mat => {
            if (data.drowsy) {
                mat.color.set(0xff0000);
            } else {
                mat.color.set(0x2E8B57);
            }
        });

    });
}, 500);

// ================= CAMERA CONTROL =================

function startCamera() {
    fetch("/start").then(() => {
        document.getElementById("videoFeed").src = "/video_feed";
        document.getElementById("status").innerText = "Status: Running";
    });
}

function stopCamera() {
    fetch("/stop").then(() => {
        document.getElementById("videoFeed").src = "";
        document.getElementById("status").innerText = "Status: Stopped";
    });
}
