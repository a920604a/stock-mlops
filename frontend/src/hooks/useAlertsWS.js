import { useEffect, useState, useRef } from "react";
import { useToast } from "@chakra-ui/react";

export function useAlertsWS() {
    const [alerts, setAlerts] = useState([]);
    const toast = useToast();
    const wsRef = useRef(null);

    useEffect(() => {
        if (wsRef.current) return; // 避免重複初始化

        const ws = new WebSocket("ws://localhost:8010/ws/alerts");
        wsRef.current = ws;

        ws.onopen = () => console.log("WebSocket connected (alerts)");
        ws.onmessage = (event) => {
            const alertData = JSON.parse(event.data);
            const description = Array.isArray(alertData.messages)
                ? alertData.messages.join("\n")
                : alertData.messages;

            console.log("Received alert:", alertData);
            setAlerts((prev) => [...prev, alertData]);

            setTimeout(() => {
                setAlerts((prev) => prev.filter((a) => a !== alertData));
            }, 8000);

            toast({
                title: `Alert ${alertData.target_date}`,
                description: description,
                status: "warning",
                duration: 7000,
                isClosable: true,
                position: "top-right",
            });
        };

        ws.onclose = () => console.log("WebSocket disconnected (alerts)");

        return () => {
            console.log("Closing WS (alerts)");
            ws.close();
            wsRef.current = null;
        };
    }, [toast]);

    return { alerts };
}
