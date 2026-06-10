package com.secureiot.doorlock_api.controller;

import com.secureiot.doorlock_api.model.User;
import com.secureiot.doorlock_api.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*", allowedHeaders = "*", methods = {RequestMethod.GET, RequestMethod.POST, RequestMethod.DELETE, RequestMethod.OPTIONS})
public class UserController {

    @Autowired
    private UserRepository userRepository;

    // 1. Loads all users into the User Management Table
    @GetMapping
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    // 2. Listens for the "Revoke Access" command from the Javascript web dashboard
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Integer id) {
        if (userRepository.existsById(id)) {
            userRepository.deleteById(id);
            return ResponseEntity.ok().build(); 
        }
        return ResponseEntity.notFound().build(); 
    }

    // 3. SECURE LOGIN: Enforces Admin-Only Access
    @PostMapping("/login")
    public ResponseEntity<?> loginUser(@RequestBody Map<String, String> credentials) {
        String email = credentials.get("email").trim();
        String password = credentials.get("password").trim();

        System.out.println("=== NEW LOGIN ATTEMPT ===");
        System.out.println("Browser sent Email: '" + email + "'");

        List<User> users = userRepository.findAll();
        for (User user : users) {
            // Check if email exists in DB
            if (user.getEmail() != null && user.getEmail().trim().equalsIgnoreCase(email)) {
                
                // Check if password matches
                if (user.getPassword() != null && user.getPassword().trim().equals(password)) {
                    
                    // NEW SECURITY GATE: Check the 'role' column!
                    if (user.getRole() != null && user.getRole().trim().equalsIgnoreCase("admin")) {
                        System.out.println("-> SUCCESS: Admin verified! Logging in.");
                        return ResponseEntity.ok().body("{\"success\": true}");
                    } else {
                        System.out.println("-> BLOCKED: Valid credentials, but user is not an admin. Role is: " + user.getRole());
                        // Return 403 Forbidden because they are a 'user', not an 'admin'
                        return ResponseEntity.status(HttpStatus.FORBIDDEN).body("{\"success\": false, \"message\": \"Access Denied: Admins Only\"}");
                    }
                } else {
                    System.out.println("-> FAILED: Invalid password.");
                }
            }
        }
        
        System.out.println("=== LOGIN REJECTED ===");
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("{\"success\": false, \"message\": \"Invalid credentials\"}");
    }
}