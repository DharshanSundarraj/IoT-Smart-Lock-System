package com.secureiot.doorlock_api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.secureiot.doorlock_api.model.User;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, Integer> {
    // This magical line tells Java to write a custom SQL query to find a user by their email!
    User findByEmail(String email);
}