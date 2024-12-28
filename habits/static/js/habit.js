const colors = [
     "#E45A84",
     "#FFD478",
     "#BA53DE",
     "#393E46",
     "#497285",
     "#3AB1C8",
     "#8DC6FF",
     "#B2E672",
     "#B17179"
 ];
 
 const app = new Vue({
     el: "#app",
     data: {
         habits: [],
         newHabit: '',
         reps: '',
         initial: 0,
         complete: 0,
         colors: colors,
         finished: false
     },
     mounted() {
         // Load habits from Django backend on component mount
         this.loadHabits();
     },
     methods: {
         async loadHabits() {
             try {
                 const response = await fetch('/api/habits/');
                 const data = await response.json();
                 this.habits = data.map(habit => ({
                     ...habit,
                     random: this.colors[Math.floor(Math.random() * this.colors.length)]
                 }));
             } catch (error) {
                 console.error('Error loading habits:', error);
             }
         },
         async addHabit() {
             if (this.newHabit && this.reps) {
                 const habitData = {
                     name: this.newHabit,
                     periodicity: 'daily',
                     description: `Complete ${this.reps} times`
                 };
 
                 try {
                     const response = await fetch('/api/habits/', {
                         method: 'POST',
                         headers: {
                             'Content-Type': 'application/json',
                             'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                         },
                         body: JSON.stringify(habitData)
                     });
 
                     if (response.ok) {
                         const habit = await response.json();
                         this.habits.push({
                             ...habit,
                             reps: this.reps,
                             initial: this.reps,
                             complete: 0,
                             random: this.colors[Math.floor(Math.random() * this.colors.length)],
                             finished: false
                         });
                         this.newHabit = '';
                         this.reps = '';
                     }
                 } catch (error) {
                     console.error('Error adding habit:', error);
                 }
             }
         },
         async removeHabit(habit) {
             try {
                 const response = await fetch(`/api/habits/${habit.id}/`, {
                     method: 'DELETE',
                     headers: {
                         'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                     }
                 });
 
                 if (response.ok) {
                     this.habits = this.habits.filter(h => h.id !== habit.id);
                 }
             } catch (error) {
                 console.error('Error removing habit:', error);
             }
         },
         async completeReps(habit) {
             try {
                 const response = await fetch(`/api/habits/${habit.id}/complete/`, {
                     method: 'POST',
                     headers: {
                         'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                     }
                 });
 
                 if (response.ok) {
                     if (habit.reps > 0) {
                         habit.reps -= 1;
                         habit.complete += 1;
                     }
                     if (habit.reps === 0) {
                         habit.finished = true;
                     }
                 }
             } catch (error) {
                 console.error('Error completing habit:', error);
             }
         }
     }
 });