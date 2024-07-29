const script = document.createElement('script');
script.src = "https://cdn.jsdelivr.net/npm/canvas-confetti@latest/dist/confetti.browser.min.js";
document.head.appendChild(script);


document.addEventListener('DOMContentLoaded', function() {
    let previousBooked = 0;

    function triggerConfetti() {
        confetti({
            particleCount: 200,
            spread: 70,
            origin: { y: 0.6 }
        });
    }

    function checkBookedDifference() {
        let bookedText = document.querySelector('#booked-text');
        if (bookedText) {
            let currentBooked = parseInt(bookedText.innerText.replace(/,/g, ''));
            if (currentBooked > previousBooked) {
                triggerConfetti();
                previousBooked = currentBooked;
            }
        }
    }

    setInterval(checkBookedDifference, 1000); // Check every second
});
