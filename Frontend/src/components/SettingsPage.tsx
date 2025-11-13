import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

//----------------Implement APIClient hook------------------------//
import { useApiClient } from "../ApiClientContext";


export function SettingsPage() {
    const navigate = useNavigate();

    // Initialize the API Client

    const apiClient = useApiClient();

    
}