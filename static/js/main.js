// Initialize Alpine.js data store
document.addEventListener('alpine:init', () => {
     Alpine.store('notifications', {
         items: [],
         unread: 0,
         
         async fetch() {
             try {
                 const response = await fetch('/api/notifications/');
                 const data = await response.json();
                 this.items = data.notifications;
                 this.unread = data.unread_count;
             } catch (error) {
                 console.error('Error fetching notifications:', error);
             }
         },
         
         async markAsRead(id) {
             try {
                 await fetch(`/api/notifications/${id}/mark-read/`, {
                     method: 'POST',
                     headers: {
                         'Content-Type': 'application/json',
                         'X-CSRFToken': getCookie('csrftoken')
                     }
                 });
                 this.items = this.items.map(item => 
                     item.id === id ? {...item, read: true} : item
                 );
                 this.unread = this.items.filter(item => !item.read).length;
             } catch (error) {
                 console.error('Error marking notification as read:', error);
             }
         }
     });
 
     Alpine.store('habits', {
         habits: [],
         loading: true,
         error: null,
 
         async fetchHabits() {
             this.loading = true;
             try {
                 const response = await fetch('/api/habits/');
                 const data = await response.json();
                 this.habits = data;
                 this.error = null;
             } catch (error) {
                 console.error('Error fetching habits:', error);
                 this.error = 'Failed to load habits';
             } finally {
                 this.loading = false;
             }
         },
 
         async completeHabit(habitId) {
             try {
                 const response = await fetch(`/api/habits/${habitId}/complete/`, {
                     method: 'POST',
                     headers: {
                         'Content-Type': 'application/json',
                         'X-CSRFToken': getCookie('csrftoken')
                     }
                 });
                 
                 const data = await response.json();
                 
                 if (response.ok) {
                     // Update local state
                     this.habits = this.habits.map(habit =>
                         habit.id === habitId
                             ? {...habit, completed_today: true, current_streak: data.streak}
                             : habit
                     );
                     
                     // Show success notification
                     showNotification('success', 'Habit completed successfully!');
                 } else {
                     throw new Error(data.message);
                 }
             } catch (error) {
                 console.error('Error completing habit:', error);
                 showNotification('error', error.message || 'Failed to complete habit');
             }
         }
     });
 });
 
 // Utility Functions
 function getCookie(name) {
     let cookieValue = null;
     if (document.cookie && document.cookie !== '') {
         const cookies = document.cookie.split(';');
         for (let i = 0; i < cookies.length; i++) {
             const cookie = cookies[i].trim();
             if (cookie.substring(0, name.length + 1) === (name + '=')) {
                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                 break;
             }
         }
     }
     return cookieValue;
 }
 
 function showNotification(type, message) {
     const notification = document.createElement('div');
     notification.className = `fixed bottom-4 right-4 p-4 rounded-md shadow-lg ${
         type === 'success' ? 'bg-green-50' : 'bg-red-50'
     }`;
     
     notification.innerHTML = `
         <div class="flex items-center">
             <div class="flex-shrink-0">
                 ${type === 'success' 
                     ? '<svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>'
                     : '<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>'
                 }
             </div>
             <div class="ml-3">
                 <p class="text-sm font-medium ${
                     type === 'success' ? 'text-green-800' : 'text-red-800'
                 }">${message}</p>
             </div>
         </div>
     `;
     
     document.body.appendChild(notification);
     setTimeout(() => {
         notification.remove();
     }, 5000);
 }
 
 // Initialize WebSocket connection for real-time notifications
 function initializeWebSocket() {
     const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
     const socket = new WebSocket(
         `${protocol}//${window.location.host}/ws/notifications/`
     );
     
     socket.onmessage = (event) => {
         const data = JSON.parse(event.data);
         if (data.type === 'notification') {
             Alpine.store('notifications').items.unshift(data.notification);
             Alpine.store('notifications').unread += 1;
             showNotification('info', data.notification.message);
         }
     };
     
     socket.onclose = () => {
         console.log('WebSocket closed. Attempting to reconnect...');
         setTimeout(initializeWebSocket, 5000);
     };
 }
 
 // Initialize on page load
 document.addEventListener('DOMContentLoaded', () => {
     initializeWebSocket();
 });