package com.calypsoproject.controllers;

import javafx.event.ActionEvent;
import javafx.event.Event;
import javafx.fxml.FXML;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleButton;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;

public class LoggerController {
    private boolean paused = false;
    @FXML private GridPane rootGrid;
    @FXML private GridPane headerGrid;
    @FXML private TextFlow textFlow;
    @FXML private ImageView pausePlay;
    @FXML private ToggleButton infoToggle;
    @FXML private ToggleButton warningToggle;
    @FXML private ToggleButton errorToggle;
    @FXML private TextField filterTextField;
    @FXML private ScrollPane scrollPane;
    private Color infoColor = Color.rgb(77, 184, 73);
    private Color warningColor = Color.rgb(247, 206, 9);
    private Color errorColor = Color.rgb(238, 123, 117);

    public LoggingFilters filters = new LoggingFilters();

    public void dockBtnMouseReleased(Event event) {
    }

    public void closeBtnMouseReleased(Event event) {
    }

    public void maximizeBtnMouseReleased(Event event) {
    }

    public void infoChanged(ActionEvent actionEvent) {
        filters.info = infoToggle.isSelected();
    }

    public void warningChanged(ActionEvent actionEvent) {
        filters.warning = warningToggle.isSelected();
    }

    public void errorChanged(ActionEvent actionEvent) {
        filters.error = errorToggle.isSelected();
    }

    public void filterChanged(Event event) {
        filters.keywords = filterTextField.getText();
    }

    public void write(int type, String orign, String message) {
        System.out.println(filters.keywords);
        if (paused || (message + orign).contains(filters.keywords) && !filters.keywords.isEmpty()) {
            return;
        }
        Text timeText = new Text("#" + String.valueOf(Math.round(System.currentTimeMillis()/1000)) + "-");
        timeText.setFill(Color.WHITESMOKE);

        Text orignText = new Text(orign);
        orignText.setFill(infoColor);

        Text typeText = new Text("unknown");
        typeText.setFill(Color.WHITESMOKE);
        switch (type){
            case 0:
                if (!filters.info) { return; }
                typeText = new Text(" (info):~$ ");
                typeText.setFill(infoColor);
                break;
            case 1:
                if (!filters.warning) { return; }
                typeText = new Text(" (warning):~$ ");
                typeText.setFill(warningColor);
                break;
            case 2:
                if (!filters.error) { return; }
                typeText = new Text(" (error):~$ ");
                typeText.setFill(errorColor);
                break;
        }

        Text messageText = new Text(message + "\n");
        messageText.setFill(Color.WHITE);

        textFlow.getChildren().addAll(timeText, orignText, typeText, messageText);
        scrollPane.setVvalue(1.0);

    }

    public void clearBtnMouseReleased(Event event) {
        textFlow.getChildren().clear();
    }

    public void showHeader() {
        rootGrid.getRowConstraints().get(0).setMinHeight(25);
        headerGrid.setVisible(true);
    }

    public void hideHeader() {
        rootGrid.getRowConstraints().get(0).setMinHeight(0);
        headerGrid.setVisible(false);
    }


    public void pausePlayBtnMouseReleased(Event event) {
        if (paused) {
            paused = false;
            pausePlay.setImage(new Image(getClass().getResource("../views/icons/pause.png").toExternalForm()));
        } else {
            paused = true;
            pausePlay.setImage(new Image(getClass().getResource("../views/icons/play.png").toExternalForm()));
        }
    }
}

class LoggingFilters {
    public boolean error = true;
    public boolean warning = true;
    public boolean info = true;
    public String keywords = "";
}