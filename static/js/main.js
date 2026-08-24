// TaskLink – main.js
// Simple JS helpers (no heavy frameworks needed)

// Auto-dismiss flash alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    var alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 4000);
});

// Set minimum datetime for deadline input to "now"
var deadlineInput = document.querySelector('input[name="deadline"]');
if (deadlineInput) {
  var now = new Date();
  // Format: YYYY-MM-DDTHH:MM
  var formatted = now.getFullYear() + '-' +
    String(now.getMonth() + 1).padStart(2, '0') + '-' +
    String(now.getDate()).padStart(2, '0') + 'T' +
    String(now.getHours()).padStart(2, '0') + ':' +
    String(now.getMinutes()).padStart(2, '0');
  deadlineInput.setAttribute('min', formatted);
}
