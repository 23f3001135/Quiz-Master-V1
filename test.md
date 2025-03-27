# Quiz Master - Manual Testing Guide

This document outlines the testing procedures to verify all functionality of the Quiz Master application.

### Chapter Management
1. Create a new chapter under a subject - should appear in chapters list
2. Edit an existing chapter - changes should be saved
3. Delete a chapter - should be removed from list
4. Verify cascade deletion - quizzes and questions should be removed

### Quiz Management
1. Create a new quiz under a chapter
   - Test with various schedule dates and durations
   - Verify all fields are saved correctly
2. Edit an existing quiz - changes should be saved
3. Delete a quiz - should be removed from list
4. Verify cascade deletion - questions and scores should be removed

### Question Management
1. Create questions for a quiz
   - Test with various options and correct answers
   - Verify all fields are saved correctly
2. Edit existing questions - changes should be saved
3. Delete questions - should be removed from list

### User Management
1. View the list of all registered users
2. Verify user details are displayed correctly

## User Functionality Testing

### Dashboard and Navigation
1. Verify all navigation links work correctly
2. Check that the user dashboard shows appropriate information
3. Verify recent quizzes are displayed correctly

### Quiz Taking
1. Test taking a quiz that hasn't started yet - should show "not available" message
2. Test taking a quiz that has ended - should show "ended" message
3. Test taking an available quiz:
   - Verify all questions are displayed
   - Submit without answering all questions - should show validation
   - Answer all questions and submit
   - Verify answers are processed correctly
   - Check score calculation is accurate

### Quiz Feedback
1. After submitting a quiz, verify feedback page shows:
   - Correct score
   - Which answers were correct/incorrect
   - The correct answers for missed questions

### Quiz History
1. Verify quiz history page shows all previous attempts
2. Check that scores are displayed correctly
3. Verify multiple attempts for the same quiz are handled properly

## Search Functionality Testing

### Admin Search
1. Test searching for users - verify results are accurate
2. Test searching for subjects - verify results are accurate
3. Test searching for quizzes - verify results are accurate
4. Test searching for questions - verify results are accurate
5. Test searches with no results - should show "no results" message

### User Search
1. Test searching for quizzes by name - verify results are accurate
2. Test searching for quizzes by description - verify results are accurate
3. Test searching by subject - verify related quizzes are shown
4. Test searches with no results - should show "no results" message

## Time-Based Testing

### Quiz Availability
1. Set up a quiz scheduled for a future time
   - Verify it shows as "not available yet" before start time
   - Verify it becomes available at the scheduled time
2. Set up a quiz with a short duration
   - Verify it shows as available during the scheduled period
   - Verify it shows as "ended" after the end time