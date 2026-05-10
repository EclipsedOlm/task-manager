// Furina viewport state machine

document.addEventListener("DOMContentLoaded", function () {
    const viewport = document.getElementById("furina-viewport");
    if (!viewport) return;

    const video = document.getElementById("furina-viewport-video");
    const frameImage = document.getElementById("furina-viewport-frame");
    const summonLayer = document.getElementById("furina-summon-layer");
    const loadingText = document.getElementById("furina-viewport-loading");
    const statusText = document.getElementById("furina-viewport-status");

    const STORAGE_KEY = "furinaViewportState_v1";
    const BASE_PATH = "/static/viewport";

const videoFiles = {
    starting: `${BASE_PATH}/furina_starting.mp4`,
    defaultTrans: `${BASE_PATH}/furina_default_trans.mp4`,
    defaultInteract: `${BASE_PATH}/furina_default_interact.mp4`,
    sleepTrans: `${BASE_PATH}/furina_sleep_trans.mp4`,
    sleepLoop: `${BASE_PATH}/furina_sleep_loop.mp4`,
    sleepRecovery: `${BASE_PATH}/furina_sleep_recovery.mp4`,
    playfulTrans: `${BASE_PATH}/furina_playful_trans.mp4`,
    playfulRecovery: `${BASE_PATH}/furina_playful_recovery.mp4`
};

    const sequences = {
        default: {
            folder: "furina_default_look",
            start: 250,
            end: 370
        },
        playful: {
            folder: "furina_playful_look",
            start: 1105,
            end: 1225
        }
    };

    const frameCache = {
        default: [],
        playful: []
    };

    const videoPreloadCache = [];

    let mode = "empty";
    let activeSequenceName = "default";
    let currentFrame = 0;
    let displayedFrame = -1;
    let targetFrame = 0;
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let idleDeadline = null;
    let animationFrameId = null;
    let statusTimeout = null;

    function getFrameCount(sequenceName) {
        const sequence = sequences[sequenceName];
        return sequence.end - sequence.start + 1;
    }

function getFrameUrl(sequenceName, frameIndex) {
    const sequence = sequences[sequenceName];
    const frameNumber = sequence.start + frameIndex;
    const paddedFrameNumber = String(frameNumber).padStart(4, "0");

    return `${BASE_PATH}/${sequence.folder}/${paddedFrameNumber}.jpg`;
}

    function preloadSequence(sequenceName) {
        if (frameCache[sequenceName].length > 0) return;

        const frameCount = getFrameCount(sequenceName);

        for (let i = 0; i < frameCount; i += 1) {
            const img = new Image();
            img.src = getFrameUrl(sequenceName, i);
            frameCache[sequenceName].push(img);
        }
    }

    function preloadVideos() {
        Object.values(videoFiles).forEach(function (src) {
            const preloadedVideo = document.createElement("video");
            preloadedVideo.src = src;
            preloadedVideo.preload = "auto";
            preloadedVideo.muted = true;
            preloadedVideo.playsInline = true;
            videoPreloadCache.push(preloadedVideo);
        });
    }

    function saveState(extra = {}) {
        const state = {
            initiated: mode !== "empty",
            mode,
            activeSequenceName,
            currentFrame,
            idleDeadline,
            savedAt: Date.now(),
            ...extra
        };

        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function loadState() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (error) {
            return null;
        }
    }

    function clearState() {
        localStorage.removeItem(STORAGE_KEY);
    }

    function showLoading(message) {
        if (!loadingText) return;
        loadingText.textContent = message;
        loadingText.classList.add("is-visible");
    }

    function hideLoading() {
        if (!loadingText) return;
        loadingText.classList.remove("is-visible");
    }

    function showStatus(message) {
        if (!statusText) return;

        statusText.textContent = message;
        statusText.classList.add("is-visible");

        clearTimeout(statusTimeout);
        statusTimeout = setTimeout(function () {
            statusText.classList.remove("is-visible");
        }, 2400);
    }

    function setViewportMood(newMood) {
        viewport.classList.remove("is-awake", "is-sleeping", "is-playful");

        if (newMood) {
            viewport.classList.add(newMood);
        }
    }

    function hideSummonLayer() {
        if (summonLayer) {
            summonLayer.classList.add("is-hidden");
        }
    }

    function showSummonLayer() {
        if (summonLayer) {
            summonLayer.classList.remove("is-hidden");
        }
    }

    function showVideo() {
        if (frameImage) {
            frameImage.classList.remove("is-visible");
        }

        if (video) {
            video.classList.add("is-visible");
        }
    }

    function showFrame() {
        if (video) {
            video.pause();
            video.classList.remove("is-visible");
        }

        if (frameImage) {
            frameImage.classList.add("is-visible");
        }
    }

    function stopTrackingLoop() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    }

    function scheduleIdleTimer() {
        const minTime = 15000;
        const maxTime = 30000;
        idleDeadline = Date.now() + minTime + Math.random() * (maxTime - minTime);
        saveState();
    }

    function chooseIdleBranch() {
        if (Math.random() < 0.5) {
            playVideoState("sleepTrans");
        } else {
            playVideoState("playfulTrans");
        }
    }

    function updateMousePosition(event) {
        mouseX = event.clientX;
        mouseY = event.clientY;
    }

    function getTargetFrame(sequenceName) {
        const frameCount = getFrameCount(sequenceName);
        const viewportRect = viewport.getBoundingClientRect();

        const isInsideViewport =
            mouseX >= viewportRect.left &&
            mouseX <= viewportRect.right &&
            mouseY >= viewportRect.top &&
            mouseY <= viewportRect.bottom;

        if (isInsideViewport) {
            return (frameCount - 1) / 2;
        }

        // Pivot is the top-right of the screen: x = max screen width, y = 0.
        // 0 degrees means the mouse is far left, 90 degrees means the mouse is down.
        const pivotX = window.innerWidth;
        const pivotY = 0;
        const dx = Math.max(0, pivotX - mouseX);
        const dy = Math.max(0, mouseY - pivotY);

        let angle = Math.atan2(dy, dx) * (180 / Math.PI);
        angle = Math.max(0, Math.min(90, angle));

        return (angle / 90) * (frameCount - 1);
    }

    function displayFrame(sequenceName, frameIndex) {
        const frameCount = getFrameCount(sequenceName);
        const safeIndex = Math.max(0, Math.min(frameCount - 1, Math.round(frameIndex)));

        if (safeIndex === displayedFrame && frameImage.classList.contains("is-visible")) return;

        displayedFrame = safeIndex;
        frameImage.src = getFrameUrl(sequenceName, safeIndex);
    }

    function startTrackingLoop(sequenceName) {
        stopTrackingLoop();
        activeSequenceName = sequenceName;

        function tick() {
            if (mode !== "default" && mode !== "playful") return;

            targetFrame = getTargetFrame(sequenceName);
            currentFrame += (targetFrame - currentFrame) * 0.13;
            displayFrame(sequenceName, currentFrame);

            if (mode === "default" && idleDeadline && Date.now() >= idleDeadline) {
                chooseIdleBranch();
                return;
            }

            animationFrameId = requestAnimationFrame(tick);
        }

        tick();
    }

    function enterDefault(options = {}) {
        const resetFrame = options.resetFrame !== false;
        const savedFrame = Number(options.savedFrame || 0);
        const savedIdleDeadline = options.idleDeadline || null;

        mode = "default";
        activeSequenceName = "default";
        setViewportMood("is-awake");
        hideSummonLayer();
        hideLoading();
        showFrame();
        preloadSequence("default");

        currentFrame = resetFrame ? 0 : savedFrame;
        displayedFrame = -1;
        displayFrame("default", currentFrame);

        if (savedIdleDeadline) {
            idleDeadline = savedIdleDeadline;
        } else {
            scheduleIdleTimer();
        }

        if (idleDeadline && Date.now() >= idleDeadline) {
            chooseIdleBranch();
            return;
        }

        saveState();
        startTrackingLoop("default");
    }

    function enterPlayful(options = {}) {
        const resetFrame = options.resetFrame !== false;
        const savedFrame = Number(options.savedFrame || 0);

        mode = "playful";
        activeSequenceName = "playful";
        idleDeadline = null;
        setViewportMood("is-playful");
        hideSummonLayer();
        hideLoading();
        showFrame();
        preloadSequence("playful");

        currentFrame = resetFrame ? 0 : savedFrame;
        displayedFrame = -1;
        displayFrame("playful", currentFrame);
        saveState();
        startTrackingLoop("playful");
    }

    function enterSleepLoop() {
        stopTrackingLoop();
        mode = "sleep_loop";
        idleDeadline = null;
        setViewportMood("is-sleeping");
        hideSummonLayer();
        showVideo();
        showStatus("Furina fell asleep. Click to wake her gently.");
        saveState();

        video.loop = true;
        video.muted = true;
        video.playsInline = true;
        video.src = videoFiles.sleepLoop;
        video.currentTime = 0;

        const playPromise = video.play();
        if (playPromise) {
            playPromise.catch(function () {
                showLoading("Click the viewport to continue.");
            });
        }
    }

    function nextAfterVideo(videoName) {
        const nextMap = {
            starting: { type: "video", name: "defaultTrans" },
            defaultTrans: { type: "default" },
            defaultInteract: { type: "video", name: "defaultTrans" },
            sleepTrans: { type: "sleep_loop" },
            sleepRecovery: { type: "video", name: "defaultTrans" },
            playfulTrans: { type: "playful" },
            playfulRecovery: { type: "video", name: "defaultTrans" }
        };

        return nextMap[videoName] || { type: "default" };
    }

    function goToNext(next) {
        if (!next) return;

        if (next.type === "video") {
            playVideoState(next.name);
        } else if (next.type === "default") {
            enterDefault({ resetFrame: true });
        } else if (next.type === "sleep_loop") {
            enterSleepLoop();
        } else if (next.type === "playful") {
            enterPlayful({ resetFrame: true });
        }
    }

    function playVideoState(videoName) {
        stopTrackingLoop();
        mode = "video";
        idleDeadline = null;
        hideSummonLayer();
        showVideo();
        hideLoading();
        setViewportMood("is-awake");
        saveState({ videoName });

        video.loop = false;
        video.muted = true;
        video.playsInline = true;
        video.src = videoFiles[videoName];
        video.currentTime = 0;

        if (videoName === "starting") {
            showStatus("The curtain rises...");
        } else if (videoName === "defaultInteract") {
            showStatus("Furina noticed you!");
        } else if (videoName === "sleepTrans") {
            showStatus("Furina is getting sleepy...");
        } else if (videoName === "playfulTrans") {
            showStatus("Furina found something interesting...");
        }

        video.onended = function () {
            video.onended = null;
            goToNext(nextAfterVideo(videoName));
        };

        video.onerror = function () {
            console.warn(`Could not play ${videoFiles[videoName]}. Check the file name and browser support.`);
            video.onerror = null;
            goToNext(nextAfterVideo(videoName));
        };

        const playPromise = video.play();
        if (playPromise) {
            playPromise.catch(function () {
                showLoading("Click the viewport to continue.");
            });
        }
    }

    function summonFurina() {
        clearState();
        preloadSequence("default");
        preloadSequence("playful");
        playVideoState("starting");
    }

    function restoreViewport() {
        const shouldReset = viewport.dataset.resetViewport === "true";

        if (shouldReset) {
            clearState();
        }

        const savedState = shouldReset ? null : loadState();

        preloadSequence("default");
        preloadSequence("playful");
        preloadVideos();

        if (!savedState || !savedState.initiated || savedState.mode === "empty") {
            mode = "empty";
            setViewportMood("");
            showSummonLayer();
            hideLoading();
            return;
        }

        hideSummonLayer();

        if (savedState.mode === "video") {
            goToNext(nextAfterVideo(savedState.videoName));
        } else if (savedState.mode === "default") {
            enterDefault({
                resetFrame: false,
                savedFrame: savedState.currentFrame || 0,
                idleDeadline: savedState.idleDeadline || null
            });
        } else if (savedState.mode === "sleep_loop") {
            enterSleepLoop();
        } else if (savedState.mode === "playful") {
            enterPlayful({
                resetFrame: false,
                savedFrame: savedState.currentFrame || 0
            });
        } else {
            mode = "empty";
            showSummonLayer();
        }
    }

    document.addEventListener("pointermove", updateMousePosition);

    viewport.addEventListener("click", function () {
        if (mode === "empty") {
            summonFurina();
        } else if (mode === "default") {
            scheduleIdleTimer();
            playVideoState("defaultInteract");
        } else if (mode === "sleep_loop") {
            playVideoState("sleepRecovery");
        } else if (mode === "playful") {
            playVideoState("playfulRecovery");
        }
    });

    window.addEventListener("beforeunload", function () {
        if (mode !== "empty") {
            saveState();
        }
    });

    restoreViewport();
});