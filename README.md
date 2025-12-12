# 🎮 GreatGames  
*A Letterboxd-style social platform for gamers.*

[![Tests](https://github.com/<YOUR_USERNAME>/greatgames/actions/workflows/test.yml/badge.svg)](https://github.com/<YOUR_USERNAME>/greatgames/actions/workflows/test.yml)
[![Latest Release](https://img.shields.io/github/v/release/<YOUR_USERNAME>/greatgames)](https://github.com/<YOUR_USERNAME>/greatgames/releases)
![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📌 Overview

**GreatGames** is a full-stack Flask web application where users can:

- Track games (wishlist, currently playing, completed)
- Leave reviews with dynamic star ratings
- Follow friends and see their gaming activity in a carousel
- Manage profiles including **profile pictures**
- Discover new games and browse by genre
- Admins can manage the game database through an admin dashboard

It is designed to function similarly to Letterboxd, but for video games.

---

## ✨ Features

### 👤 User System
- Registration & login  
- Profile editing (name, bio, profile picture upload)  
- Follow/unfollow users  
- See friends’ activity  

### 🎮 Game Tracking
- Add games to lists  
- Statuses: Wishlist / Currently Playing / Completed  
- Display game cards in responsive grids  

### ⭐ Reviews
- 1–10 star rating system with hover animations  
- Anonymous posting option  
- Display reviews on game pages  

### 📰 Activity Feed
- Records:
  - List updates  
  - Reviews  
  - Completed games  
- Friend activity carousel  
- User activity shown on home and profile pages  

### 🛠 Admin Tools
- Add/edit/remove games  
- Manage data records  

### 🔐 Automated Tests (GitHub Actions)
- Pytest suite for:
  - Authentication
  - Protected routes
  - Admin routes
  - Basic rendering & routing  

### 🚀 CI/CD
- Automatic test execution on push  
- Badges displaying build status & releases  

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/pabluchiyague/greatgames.git
cd greatgames
