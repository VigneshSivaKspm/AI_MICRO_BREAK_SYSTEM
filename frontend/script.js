// API Configuration
const API_BASE = 'http://localhost:2050/api/v1';

// Global state
let monitoringActive = false;
let currentUserId = 1;
let updateInterval = null;

// ==================== TAB NAVIGATION ====================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        
        // Show selected tab
        const tabId = item.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// ==================== MONITORING CONTROLS ====================

document.getElementById('btn-start-monitoring')?.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/monitoring/start`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId })
        });
        const data = await response.json();
        
        if (response.ok) {
            monitoringActive = true;
            document.getElementById('status-indicator').textContent = '🟢 Active';
            document.getElementById('status-indicator').style.color = '#28a745';
            showAlert('✅ Monitoring started successfully', 'success');
            startDataUpdates();
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error starting monitoring:', error);
        showAlert('Failed to start monitoring', 'danger');
    }
});

document.getElementById('btn-stop-monitoring')?.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/monitoring/stop`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId })
        });
        const data = await response.json();
        
        if (response.ok) {
            monitoringActive = false;
            document.getElementById('status-indicator').textContent = '🔴 Idle';
            document.getElementById('status-indicator').style.color = '#dc3545';
            showAlert('⏹️ Monitoring stopped', 'info');
            stopDataUpdates();
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error stopping monitoring:', error);
        showAlert('Failed to stop monitoring', 'danger');
    }
});

// ==================== BREAK CONTROLS ====================

document.getElementById('btn-take-break')?.addEventListener('click', async () => {
    await enforceBreak();
});

document.getElementById('btn-enforce-break')?.addEventListener('click', async () => {
    await enforceBreak();
});

async function enforceBreak() {
    try {
        const duration = parseInt(document.getElementById('break-duration')?.value || 5);
        
        const response = await fetch(`${API_BASE}/breaks/enforce`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duration: duration,
                break_type: duration <= 3 ? 'micro' : (duration <= 5 ? 'regular' : 'long'),
                lock_screen: false,
                mute_input: false
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`Break started for ${duration} minutes`, 'success');
            updateBreakStatus();
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error enforcing break:', error);
        showAlert('Failed to enforce break', 'danger');
    }
}

// ==================== RECOMMENDATIONS ====================

document.getElementById('btn-get-recommendations')?.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/recommendations?user_id=${currentUserId}`);
        const data = await response.json();
        
        if (response.ok) {
            displayRecommendations(data.recommendations);
            showAlert('Recommendations updated', 'success');
        } else {
            showAlert('Failed to get recommendations', 'danger');
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
        showAlert('Failed to get recommendations', 'danger');
    }
});

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p>No recommendations available at this time.</p>';
        return;
    }
    
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        const title = rec.activity || rec.title || rec.category;
        const duration = rec.duration_min || rec.duration || 5;
        
        card.innerHTML = `
            <h4>${title}</h4>
            <p class="description">${rec.reason || rec.description || ''}</p>
            <p class="duration">⏱️ ${duration} minute${duration > 1 ? 's' : ''}</p>
            <button class="btn btn-small btn-primary" onclick="startActivity('${title}', ${duration})">Start Activity</button>
        `;
        container.appendChild(card);
    });
}

async function startActivity(activityName, durationMin) {
    try {
        const duration = durationMin || 5;
        const response = await fetch(`${API_BASE}/breaks/enforce`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duration: duration,
                break_type: 'personalized',
                lock_screen: false,
                mute_input: false,
                reason: activityName
            })
        });
        
        if (response.ok) {
            showAlert(`Activity started: ${activityName} (${duration} min)`, 'success');
            updateBreakStatus();
        } else {
            const data = await response.json();
            showAlert(data.error || 'Failed to start activity', 'danger');
        }
    } catch (error) {
        console.error('Error starting activity:', error);
        showAlert('Error starting activity', 'danger');
    }
}

// Make globally available
window.startActivity = startActivity;

async function stopCurrentBreak() {
    try {
        const response = await fetch(`${API_BASE}/breaks/stop`, { method: 'POST' });
        if (response.ok) {
            showAlert('Break cancelled', 'info');
            updateBreakStatus();
        }
    } catch (error) {
        console.error('Error stopping break:', error);
    }
}

// ==================== DATA UPDATES ====================

let updateRetryCount = 0;
const MAX_RETRY_COUNT = 3;

function startDataUpdates() {
    updateInterval = setInterval(async () => {
        if (updateRetryCount >= MAX_RETRY_COUNT) {
            console.warn('Too many update failures, slowing down polling');
            await updateAllDataWithRetry();
        } else {
            await updateAllData();
        }
    }, 2000);  // Changed from 30s to 2s for real-time timer updates
    
    // Initial update immediately
    updateAllData();
}

function stopDataUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
    updateRetryCount = 0;
}

async function updateAllData() {
    try {
        // Run updates in parallel but with proper error handling
        const [activityResult, fatigueResult, breakResult, analyticsResult] = await Promise.allSettled([
            updateActivityData(),
            updateFatigueData(),
            updateBreakStatus(),
            loadAnalytics()
        ]);
        
        // Check for failures
        let hasFailures = false;
        [activityResult, fatigueResult, breakResult, analyticsResult].forEach((result, index) => {
            if (result.status === 'rejected') {
                console.error(`Update ${index} failed:`, result.reason);
                hasFailures = true;
            }
        });
        
        if (hasFailures) {
            updateRetryCount++;
        } else {
            updateRetryCount = 0;  // Reset on success
        }
        
    } catch (error) {
        console.error('Error in updateAllData:', error);
        updateRetryCount++;
    }
}

async function updateAllDataWithRetry() {
    // Slower updates when there are failures
    await new Promise(resolve => setTimeout(resolve, 5000));  // Wait 5 seconds
    await updateAllData();
}

async function updateActivityData() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);  // Increased to 15s
        
        const response = await fetch(`${API_BASE}/activity/current?user_id=${currentUserId}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('mouse-clicks').textContent = data.total_mouse_clicks || 0;
            document.getElementById('keyboard-presses').textContent = data.total_keyboard_presses || 0;
            document.getElementById('idle-time').textContent = Math.round((data.total_idle_time || 0));
            
            // Format screen time
            const screenSeconds = data.screen_time || 0;
            const mins = Math.floor(screenSeconds / 60);
            const secs = Math.floor(screenSeconds % 60);
            const hrs = Math.floor(mins / 60);
            const displayTime = hrs > 0 ? 
                `${hrs}h ${mins % 60}m ${secs}s` : 
                `${mins}m ${secs}s`;
            
            const screenTimeElem = document.getElementById('screen-time-display');
            if (screenTimeElem) screenTimeElem.textContent = displayTime;
            
            // Use activity_level from API
            const activityLevel = Math.round(data.activity_level || 0);
            document.getElementById('activity-progress').style.width = activityLevel + '%';
            document.getElementById('activity-level').textContent = activityLevel + '%';
            
            document.getElementById('activity-level-detail').textContent = 
                activityLevel > 70 ? 'High' : (activityLevel > 30 ? 'Normal' : 'Low');
        } else {
            console.warn('Activity data request failed:', response.status);
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.warn('Activity data request timed out');
        } else {
            console.error('Error updating activity data:', error);
        }
        // Don't show error alerts for data update failures
        throw error;  // Re-throw to be caught by retry logic
    }
}

async function updateFatigueData() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);  // Increased to 15s
        
        const response = await fetch(`${API_BASE}/fatigue/status?user_id=${currentUserId}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (response.ok) {
            const fatigueScore = Math.round((data.fatigue_score || 0) * 100);
            document.getElementById('fatigue-progress').style.width = fatigueScore + '%';
            document.getElementById('fatigue-level').textContent = fatigueScore + '%';
            document.getElementById('fatigue-score').textContent = (data.fatigue_score || 0).toFixed(2);
            
            const eyeStrain = Math.round((data.eye_strain_level || 0) / 10 * 100);
            document.getElementById('eye-strain-progress').style.width = eyeStrain + '%';
            document.getElementById('eye-strain').textContent = eyeStrain + '%';
            
            document.getElementById('eye-strain-level').textContent = 
                eyeStrain > 60 ? 'High' : (eyeStrain > 30 ? 'Medium' : 'Low');
            
            const postureScore = Math.round((data.posture_score || 0.7) * 100);
            document.getElementById('posture-progress').style.width = postureScore + '%';
            document.getElementById('posture-score').textContent = postureScore + '%';
            document.getElementById('posture-status').textContent = 
                postureScore > 70 ? 'Good' : 'Needs Attention';
            
            document.getElementById('blink-rate').textContent = (data.blink_rate || 18).toFixed(0) + ' blinks/min';
            document.getElementById('facial-expression').textContent = data.facial_expression || 'Neutral';
            
            // Show alerts if needed (but not too frequently)
            if (data.alert_generated && Date.now() - (window.lastFatigueAlert || 0) > 300000) {  // Max once per 5 minutes
                showAlert('⚠️ Fatigue detected. Consider taking a break.', 'warning');
                window.lastFatigueAlert = Date.now();
            }
        } else {
            console.warn('Fatigue data request failed:', response.status);
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.warn('Fatigue data request timed out');
        } else {
            console.error('Error updating fatigue data:', error);
        }
        throw error;  // Re-throw to be caught by retry logic
    }
}

async function updateBreakStatus() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        
        // Add timestamp to prevent caching
        const response = await fetch(`${API_BASE}/breaks/status?user_id=${currentUserId}&t=${Date.now()}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (response.ok) {
            const infoDiv = document.getElementById('enforcement-info');
            
            // Handle active break timer
            if (data.is_enforcing && data.time_remaining > 0) {
                const mins = Math.floor(data.time_remaining / 60);
                const secs = data.time_remaining % 60;
                infoDiv.innerHTML = `
                    <div class="enforcement-active" style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107;">
                        <h4 style="color: #856404; margin-bottom: 5px;">🔒 Break in Progress</h4>
                        <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">${mins}m ${secs}s remaining</p>
                        <button class="btn btn-small btn-danger" onclick="stopCurrentBreak()">Cancel Break</button>
                    </div>
                `;
                return; // Skip the rest of the status update
            }

            if (data.breaks_today && data.breaks_today > 0) {
                infoDiv.innerHTML = `
                    <div class="enforcement-active">
                        <p>Breaks taken today: ${data.breaks_today}</p>
                        <p>Compliance rate: ${Math.round((data.compliance_rate || 0) * 100)}%</p>
                        <div class="progress-bar">
                            <div class="progress" style="width: ${Math.round((data.compliance_rate || 0) * 100)}%"></div>
                        </div>
                    </div>
                `;
            } else {
                infoDiv.innerHTML = `
                    <div class="enforcement-inactive">
                        <p>No breaks taken today</p>
                        <p>Remember to take regular breaks!</p>
                    </div>
                `;
            }
        } else {
            console.warn('Break status request failed:', response.status);
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.warn('Break status request timed out');
        } else {
            console.error('Error updating break status:', error);
        }
        throw error;  // Re-throw to be caught by retry logic
    }
}

// ==================== ANALYTICS ====================

async function loadAnalytics() {
    try {
        const dailyResponse = await fetch(`${API_BASE}/analytics/daily?user_id=${currentUserId}`);
        const dailyData = await dailyResponse.json();
        
        if (dailyResponse.ok) {
            const productivityScore = Math.round(dailyData.productivity_score || 0);
            const workTime = dailyData.total_work_time || 0;
            const breakTime = dailyData.total_break_time || 0;
            const complianceRate = (dailyData.break_compliance_rate || 0);
            const focusScore = Math.round(dailyData.focus_score || 0);
            
            document.getElementById('productivity-score').textContent = productivityScore + '%';
            document.getElementById('work-time').textContent = formatTime(workTime);
            document.getElementById('break-time').textContent = formatTime(breakTime);
            document.getElementById('compliance-rate').textContent = Math.round(complianceRate * 100) + '%';
            document.getElementById('focus-score').textContent = focusScore + '%';
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}min`;
}

// ==================== ALERTS ====================

function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    alertsContainer.insertBefore(alert, alertsContainer.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 AI Micro Break System Dashboard Loaded - Production Ready');
    
    // Initialize status indicator
    const statusIndic = document.getElementById('status-indicator');
    if (statusIndic) {
        statusIndic.textContent = '🔴 Idle';
        statusIndic.style.color = '#dc3545';
    }
    
    // Load initial data
    loadAnalytics();
});
