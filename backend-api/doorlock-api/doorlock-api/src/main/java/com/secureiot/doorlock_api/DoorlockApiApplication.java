package com.secureiot.doorlock_api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import java.util.Map;

@SpringBootApplication
@RestController 
public class DoorlockApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(DoorlockApiApplication.class, args);
    }

    // ==============================================================================
    // GLOBAL CORS CONFIGURATION 
    // ==============================================================================
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**") 
                        .allowedOriginPatterns("*") 
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS") 
                        .allowedHeaders("*")
                        .allowCredentials(false);
            }
        };
    }

    // ==============================================================================
    // HARDWARE RELAY ENDPOINT (BULLETPROOF VIVA VERSION)
    // Supports both GET and POST. Makes 't' optional so the API never crashes.
    // ==============================================================================
    @RequestMapping(value = "/api/hardware/unlock", method = {RequestMethod.GET, RequestMethod.POST})
    public ResponseEntity<?> remoteUnlock(@RequestParam(defaultValue = "5") int t) {
        
        System.out.println("\n------------------------------------------------");
        System.out.println("[SERVER LOG] Manual Override Signal Received from App!");
        
        RestTemplate restTemplate = new RestTemplate();
        
        // The active ESP32 IP Address
        String espUrl = "http://10.220.103.206/unlock?t=" + t; 
        
        System.out.println("[SERVER LOG] Attempting to push command to ESP32: " + espUrl);
        
        try {
            // Push the command to the hardware
            restTemplate.getForObject(espUrl, String.class);
            
            System.out.println("[SERVER LOG] SUCCESS: ESP32 Relay Triggered!");
            System.out.println("------------------------------------------------\n");
            
            return ResponseEntity.ok(Map.of("success", true, "message", "Hardware unlocked via Server Relay"));
        } catch (Exception e) {
            System.out.println("[SERVER LOG] ERROR: Could not reach ESP32 at " + espUrl);
            System.out.println("------------------------------------------------\n");
            
            return ResponseEntity.status(500).body(Map.of("success", false, "message", "Java Server could not reach ESP32"));
        }
    }
}