package com.example.demo.controller;

import com.example.demo.model.User;
import com.example.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;

    @PostMapping("/sign-up")
    public String signUp(@RequestBody User user) {
        if (userService.findByUsername(user.getUsername()) != null) {
            return "Username already exists";
        }
        userService.save(user);
        return "User registered successfully";
    }
}
