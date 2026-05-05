// This handles the custom cursor, ripple clicks, sparkle bursts, modal closing, and auto-dismissing toast notifications

document.addEventListener("DOMContentLoaded", function () {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const hasFinePointer = window.matchMedia("(pointer: fine)").matches;

    // Custom cursor
    if (hasFinePointer && !prefersReducedMotion) {
        document.body.classList.add("furina-custom-cursor");

        const cursorDot = document.createElement("div");
        cursorDot.className = "furina-cursor-dot";

        const cursorRing = document.createElement("div");
        cursorRing.className = "furina-cursor-ring";

        document.body.appendChild(cursorRing);
        document.body.appendChild(cursorDot);

        let mouseX = window.innerWidth / 2;
        let mouseY = window.innerHeight / 2;
        let ringX = mouseX;
        let ringY = mouseY;

        function moveCursor() {
            ringX += (mouseX - ringX) * 0.18;
            ringY += (mouseY - ringY) * 0.18;

            cursorDot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
            cursorRing.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;

            requestAnimationFrame(moveCursor);
        }

        document.addEventListener("pointermove", function (event) {
            mouseX = event.clientX;
            mouseY = event.clientY;
        });

        document.addEventListener("pointerdown", function () {
            cursorRing.classList.add("is-clicking");
            cursorDot.classList.add("is-clicking");
        });

        document.addEventListener("pointerup", function () {
            cursorRing.classList.remove("is-clicking");
            cursorDot.classList.remove("is-clicking");
        });

        moveCursor();
    }

    // Google-ish ripple effect for buttons/cards/labels
    const rippleSelector = [
        ".cute-btn",
        ".primary-btn",
        ".secondary-btn",
        ".primary-action-btn",
        ".danger-btn",
        ".theatre-tab",
        ".performance-card",
        ".troupe-card",
        ".join-troupe-card",
        ".icon-choice-card",
        ".mini-link-btn",
        ".nav-user-profile",
        ".navlinks a",
        ".auth-switch a",
        ".modal-close",
        ".chat-input-row button",
        "button"
    ].join(", ");

    document.querySelectorAll(rippleSelector).forEach(function (element) {
        element.classList.add("furina-ripple-ready");
    });

    document.addEventListener("pointerdown", function (event) {
        const target = event.target.closest(rippleSelector);
        if (!target) return;

        const rect = target.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2.15;
        const ripple = document.createElement("span");

        ripple.className = "furina-ripple";
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

        target.appendChild(ripple);
        ripple.addEventListener("animationend", function () {
            ripple.remove();
        });
    });

    // Tiny sparkle burst on clicks. It skips form fields so typing does not feel annoying
    document.addEventListener("pointerdown", function (event) {
        if (prefersReducedMotion) return;
        if (event.target.closest("input, textarea, select, option")) return;

        const sparkleCount = 7;
        const sparkleSymbols = ["✦", "✧", "•"];

        for (let i = 0; i < sparkleCount; i += 1) {
            const sparkle = document.createElement("span");
            const angle = (Math.PI * 2 * i) / sparkleCount + Math.random() * 0.55;
            const distance = 28 + Math.random() * 34;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;

            sparkle.className = "furina-click-spark";
            sparkle.textContent = sparkleSymbols[Math.floor(Math.random() * sparkleSymbols.length)];
            sparkle.style.left = `${event.clientX}px`;
            sparkle.style.top = `${event.clientY}px`;
            sparkle.style.setProperty("--spark-x", `${x}px`);
            sparkle.style.setProperty("--spark-y", `${y}px`);
            sparkle.style.animationDelay = `${Math.random() * 70}ms`;

            document.body.appendChild(sparkle);
            sparkle.addEventListener("animationend", function () {
                sparkle.remove();
            });
        }
    });

    document.querySelectorAll(".furina-toast").forEach(function (toast, index) {
        const closeButton = toast.querySelector(".furina-toast-close");
        const timeout = Number(toast.dataset.timeout || 3600) + index * 240;

        function dismissToast() {
            toast.classList.add("is-leaving");
            setTimeout(function () {
                toast.remove();
            }, 320);
        }

        if (closeButton) {
            closeButton.addEventListener("click", dismissToast);
        }

        setTimeout(dismissToast, timeout);
    });

    document.querySelectorAll("form").forEach(function (form) {
        form.addEventListener("submit", function () {
            const button = form.querySelector("button[type='submit'], .primary-btn");
            if (button) {
                button.classList.add("is-submitting");
            }
        });
    });

    const overlayToToggle = {
        "add-performance-modal": "add-performance-toggle",
        "create-troupe-modal": "create-troupe-toggle",
        "join-troupe-modal": "join-troupe-toggle",
        "task-icon-picker-modal": "task-icon-picker-toggle",
        "group-icon-picker-modal": "group-icon-picker-toggle",
        "profile-picker-modal": "profile-picker-toggle"
    };

    function getToggleForOverlay(overlay) {
        if (!overlay) return null;

        const previousElement = overlay.previousElementSibling;
        if (previousElement && previousElement.classList.contains("modal-toggle")) {
            return previousElement;
        }

        for (const className in overlayToToggle) {
            if (overlay.classList.contains(className)) {
                return document.getElementById(overlayToToggle[className]);
            }
        }

        return null;
    }

    function closeOverlay(overlay) {
        const toggle = getToggleForOverlay(overlay);

        if (toggle) {
            toggle.checked = false;
        }
    }

    function createUnsavedWarning(targetToggle) {
        const existingWarning = document.querySelector(".furina-unsaved-confirm-modal");
        if (existingWarning) {
            existingWarning.remove();
        }

        const warningOverlay = document.createElement("div");
        warningOverlay.className = "modal-overlay furina-unsaved-confirm-modal";

        warningOverlay.innerHTML = `
            <div class="modal-card notification-card confirm-card unsaved-confirm-card">
                <button type="button" class="modal-close unsaved-warning-cancel">×</button>

                <div class="notification-content">
                    <img
                        src="/static/images/furina_shocked.png"
                        alt="Shocked Furina"
                        class="notification-furina-img"
                    >

                    <div>
                        <p class="eyebrow">Leaving So Soon?</p>
                        <h2>Are you sure you want to exit?</h2>
                        <p class="notification-text">
                            Unsaved changes will be lost!
                        </p>
                    </div>
                </div>

                <div class="modal-actions notification-actions">
                    <button type="button" class="cute-btn secondary-btn unsaved-warning-cancel">
                        Cancel
                    </button>

                    <button type="button" class="cute-btn danger-btn unsaved-warning-exit">
                        Exit
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(warningOverlay);

        warningOverlay.querySelectorAll(".unsaved-warning-cancel").forEach(function (button) {
            button.addEventListener("click", function () {
                warningOverlay.remove();
            });
        });

        warningOverlay.querySelector(".unsaved-warning-exit").addEventListener("click", function () {
            if (targetToggle) {
                targetToggle.checked = false;
            }

            warningOverlay.remove();
        });

        warningOverlay.addEventListener("click", function (event) {
            if (event.target === warningOverlay) {
                warningOverlay.remove();
            }
        });

        warningOverlay.querySelectorAll(rippleSelector).forEach(function (element) {
            element.classList.add("furina-ripple-ready");
        });
    }

    function shouldWarnBeforeClosing(toggle) {
        if (!toggle) return false;

        return toggle.id === "add-performance-toggle" || toggle.id === "create-troupe-toggle";
    }

    function requestModalClose(overlay) {
        const toggle = getToggleForOverlay(overlay);

        if (shouldWarnBeforeClosing(toggle)) {
            createUnsavedWarning(toggle);
        } else {
            closeOverlay(overlay);
        }
    }

    // Clicking blank space outside a popup closes most popups
    document.addEventListener("click", function (event) {
        const overlay = event.target.closest(".modal-overlay");

        if (!overlay) return;

        if (event.target !== overlay) return;

        if (overlay.classList.contains("auth-notification-modal")) return;

        const toggle = getToggleForOverlay(overlay);

        if (shouldWarnBeforeClosing(toggle)) {
            return;
        }

        if (overlay.classList.contains("furina-confirm-modal")) {
            closeOverlay(overlay);
            return;
        }

        requestModalClose(overlay);
    });

    document.addEventListener("click", function (event) {
        const closeButton = event.target.closest(".modal-close");

        if (!closeButton) return;

        const overlay = closeButton.closest(".modal-overlay");
        const toggle = getToggleForOverlay(overlay);

        if (!overlay || !shouldWarnBeforeClosing(toggle)) return;

        event.preventDefault();
        event.stopPropagation();

        createUnsavedWarning(toggle);
    });
});