package com.secureiot.doorlock_api.controller;

import com.secureiot.doorlock_api.model.AccessLog;
import com.secureiot.doorlock_api.repository.AccessLogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/logs")
@CrossOrigin(origins = "*") // Allows your HTML frontend to fetch this data
public class AccessLogController {

    @Autowired
    private AccessLogRepository accessLogRepository;

    // 1. THE GET ROUTE: Fetches data from MySQL for your HTML Dashboard
    @GetMapping
    public List<AccessLog> getAllLogs() {
        return accessLogRepository.findAll();
    }

    // 2. THE POST ROUTE: Listens for the AI Camera Trigger from Python
    @PostMapping
    public ResponseEntity<?> receiveAccessLog(@RequestBody Map<String, String> payload) {
        String email = payload.get("userEmail");
        String status = payload.get("accessStatus");
        
        System.out.println("\n=========================================");
        System.out.println("🚨 AI CAMERA TRIGGER DETECTED 🚨");
        System.out.println("User Email : " + email);
        System.out.println("Status     : " + status);
        System.out.println("=========================================\n");

        // Create a new log entry and save it to the database
        AccessLog newLog = new AccessLog();
        newLog.setUserEmail(email);
        newLog.setAccessStatus(status);
        
        // Java gets the exact current date and time
        newLog.setTimestamp(java.time.LocalDateTime.now().toString()); 
        
        accessLogRepository.save(newLog);
        
        return ResponseEntity.ok("Log successfully received by Java!");
    }
}