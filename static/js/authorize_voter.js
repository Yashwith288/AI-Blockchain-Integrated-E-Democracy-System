let otpCountdown;
    let timeLeft = 60;

    function startOtpTimer() {
        const timerText = document.getElementById("otp-timer");
        const timerValue = document.getElementById("timer");
        const otpBtn = document.getElementById("otpBtn");

        timerText.style.display = "block";
        otpBtn.disabled = true;
        otpBtn.innerText = "Resend OTP in 60s";

        timeLeft = 60;
        timerValue.innerText = timeLeft;

        otpCountdown = setInterval(() => {
            timeLeft--;
            timerValue.innerText = timeLeft;
            otpBtn.innerText = `Resend OTP in ${timeLeft}s`;

            if (timeLeft <= 0) {
                clearInterval(otpCountdown);
                otpBtn.disabled = false;
                otpBtn.innerText = "Resend OTP";
            }
        }, 1000);
    }

    function handleOtpSubmit(event) {
        const clickedButton = document.activeElement;

        if (clickedButton && clickedButton.value === "request_otp") {
            startOtpTimer();
        }
    }