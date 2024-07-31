const script = document.createElement('script');
script.src = "https://cdn.jsdelivr.net/npm/canvas-confetti@latest/dist/confetti.browser.min.js";
document.head.appendChild(script);

document.addEventListener('DOMContentLoaded', function() {
    let previousBooked = 0;

    const colors = [
        '#ff6347', // Tomato
        '#ffea00', // Yellow
        '#32cd32', // Lime Green
        '#00bfff', // Deep Sky Blue
        '#ff69b4', // Hot Pink
        '#ff4500', // Orange Red
        '#adff2f', // Green Yellow
        '#1e90ff', // Dodger Blue
        '#ff1493', // Deep Pink
        '#00fa9a', // Medium Spring Green
        '#d2691e', // Chocolate
        '#ff8c00', // Dark Orange
        '#8a2be2', // Blue Violet
        '#7cfc00', // Lawn Green
        '#ff1493'  // Deep Pink
    ];

    const poundShapes = colors.map(color => confetti.shapeFromText({
        text: '£',
        scalar: 3,
        color: color,
        fontfamily: 'Lato',
    }));

    function triggerConfetti() {
        confetti({
            particleCount: 300,
            spread: 90,
            origin: { y: 0.9 },
            ticks: 500,
            scalar: 1.2,
            startVelocity: 70
        });
    }

    function triggerPoundConfetti() {
        poundShapes.forEach(shape => {
            confetti({
                shapes: [shape],
                particleCount: 10,
                spread: 100,
                origin: { y: 0.9 },
                ticks: 500,
                scalar: 3.5,
                startVelocity: 80
            });
        });
    }

    function checkBookedDifference() {
        let bookedText = document.querySelector('#booked-text');
        if (bookedText) {
            let currentBooked = parseInt(bookedText.innerText.replace(/,/g, ''));
            if (currentBooked > previousBooked) {
                triggerConfetti();
                triggerPoundConfetti();
                previousBooked = currentBooked;
            }
        }
    }

    setInterval(checkBookedDifference, 1000);
});
