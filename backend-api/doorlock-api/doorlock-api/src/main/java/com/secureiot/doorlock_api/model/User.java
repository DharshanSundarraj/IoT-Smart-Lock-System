package com.secureiot.doorlock_api.model;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonProperty; // ADD THIS IMPORT
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id") 
    @JsonProperty("id") // Tells the HTML frontend exactly what to call this
    private Integer user_id;

    @Column(name = "fullname", nullable = false) 
    @JsonProperty("fullname") // Forces the JSON to match your HTML perfectly
    private String full_name;

    @Column(name = "email", unique = true)
    @JsonProperty("email")
    private String email;

    @Column(name = "password") 
    private String password;

    @Column(name = "role")
    @JsonProperty("role")
    private String role;
    
    @Transient // Ignores this entirely because it's not in MySQL
    private String status;
    
    @Column(name = "date_registered", insertable = false, updatable = false)
    @JsonProperty("date_registered")
    private LocalDateTime date_registered;

    @Column(name = "face_encoding", columnDefinition = "json")
    private String face_encoding;

    // Default Constructor
    public User() {}

    // Getters and Setters
    public Integer getUser_id() { return user_id; }
    public void setUser_id(Integer user_id) { this.user_id = user_id; }

    public String getFull_name() { return full_name; }
    public void setFull_name(String full_name) { this.full_name = full_name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getDate_registered() { return date_registered; }
    public void setDate_registered(LocalDateTime date_registered) { this.date_registered = date_registered; }

    public String getFace_encoding() { return face_encoding; }
    public void setFace_encoding(String face_encoding) { this.face_encoding = face_encoding; }
}